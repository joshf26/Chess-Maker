from importlib import import_module
from typing import Dict
from uuid import uuid4

from color import Color
from game import Game
from network import Network, Connection
from pack import load_packs
from ply import ply_to_json

PORT = 8000


def main():
    network = Network()
    games: Dict[str, Game] = {}
    packs = load_packs()

    def make_game_metadata(connection: Connection) -> dict:
        return {game_id: {
            'name': game.name,
            'creator': game.owner.nickname,
            'board': game.board.name,
            'available_colors': list(map(lambda color: color.value, game.get_available_colors())),
            'total_players': len(game.board.colors),
            'playing_as': None if (
                  color := game.players.connection_to_color.get(connection, None)
            ) is None else color.value,
        } for game_id, game in games.items()}

    async def send_metadata_update_to_all():
        for connection in network.connections:
            await connection.run('update_game_metadata', {
                'game_metadata': make_game_metadata(connection),
            })

    async def send_game_update_to_subscribers(game_id: str):
        game = games[game_id]
        game_data = game.get_full_data()
        game_data['id'] = game_id

        for connection in game.subscribers:
            await connection.run('full_game_data', game_data)

    @network.command()
    async def login(connection: Connection, nickname: str):
        nicknames = {connection.nickname for connection in network.connections}
        while nickname in nicknames:
            nickname += ' 2'

        print(f'{nickname} logged in!')
        connection.nickname = nickname

        await connection.run('set_nickname', {'nickname': nickname})
        await send_pieces(connection)

    @network.command()
    async def send_pieces(connection: Connection):
        piece_data = {
            pack: {piece.name: {
                'image': piece.image,
            } for piece in pieces}
            for pack, (boards, pieces) in packs.items()
        }

        await connection.run('update_pieces', {
            'pieces': piece_data,
        })

    @network.command()
    async def get_games(connection: Connection):
        await connection.run('update_game_metadata', {
            'game_metadata': make_game_metadata(connection),
        })

    @network.command()
    async def create_game(connection: Connection, name: str, pack: str, board: str):
        try:
            pack = import_module(f'packs.{pack}')
        except ModuleNotFoundError:
            await connection.error(f'Package "{pack}" does not exist.')
            return

        try:
            board_class = getattr(pack, board)
        except AttributeError:
            await connection.error(f'Board {board} does not exist in package {pack}.')
            return

        # Ensure there are no duplicate game ids.
        while (game_id := str(uuid4())) in games:
            pass

        games[game_id] = Game(name, connection, board_class(), network)

        await connection.send({
            'game_id': game_id,
        })

        await send_metadata_update_to_all()

    @network.command()
    async def delete_game(connection: Connection, game_id: str):
        if game_id not in games:
            await connection.error('Game does not exist.')
            return

        game = games[game_id]

        if game.owner != connection:
            await connection.error('Only the owner of this game can delete it.')
            return

        del games[game_id]

        await send_metadata_update_to_all()

    @network.command()
    async def subscribe_to_game(connection: Connection, game_id: str):
        if game_id not in games:
            await connection.error('Game does not exist.')
            return

        game = games[game_id]
        game.add_subscriber(connection)

        game_data = game.get_full_data()
        game_data['id'] = game_id

        await connection.run('full_game_data', game_data)

    @network.command()
    async def join_game(connection: Connection, game_id: str, color: int):
        if game_id not in games:
            await connection.error('Game id does not exist.')
            return

        game = games[game_id]

        if connection in game.players:
            await connection.error('Player is already in this game.')
            return

        color_object = next(filter(lambda x: x.value == color, Color.__iter__()), None)

        if color_object is None:
            await connection.error('Color does not exist.')
            return

        if color_object in game.players:
            await connection.error('That color is already taken in this game.')
            return

        game.add_player(connection, color_object)

        await connection.run('joined_game', {
            'game_id': game_id,
            'color': color,
        })

        await send_metadata_update_to_all()

    ''' Note to Self:
    
    This should work by the user first requesting all available plies (ordered).
    Then the user can send back the index of which ply they are interested in for
    each specific from/to pair.
    '''

    @network.command()
    async def get_plies(connection: Connection, game_id: str, from_row: int, from_col: int, to_row: int, to_col: int):
        if game_id not in games:
            await connection.error('Game id does not exist.')
            return

        game = games[game_id]
        plies = game.get_plies((from_row, from_col), (to_row, to_col))

        if len(plies) == 1:
            # There is only one ply available, so just apply it immediately.
            game.apply_ply(plies[0])
            await send_game_update_to_subscribers(game_id)
        elif len(plies) > 1:
            # There are multiple plies available, so present the user with a choice.
            # TODO
            result = [ply_to_json(ply) for ply in plies]

            await connection.run('plies', {
                'plies': result,
            })

    @network.command()
    async def submit_turn(connection: Connection, game_id: str, from_row: int, from_col: int, to_row: int, to_col: int):
        if game_id not in games:
            await connection.error('Game id does not exist.')
            return

        game = games[game_id]

        if connection not in game.players.values():
            await connection.error('Player is not in this game.')
            return

        color = game.players.get_color(connection)

        if game.current_color() != color:
            await connection.error("It is not this player's turn.")
            return

        from_pos = (from_row, from_col)
        to_pos = (to_row, to_col)

        if from_pos not in game.board.tiles:
            await connection.error('There is no piece on that tile.')
            return

        if game.board.tiles[from_pos].color != color:
            await connection.error("That piece does not belong to this player.")
            return

        if game.board.tiles[from_pos].ply_types(from_pos, to_pos, game):
            pass  # TODO

    network.serve(8000)


if __name__ == '__main__':
    main()
