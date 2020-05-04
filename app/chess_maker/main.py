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

    @network.command()
    async def login(connection: Connection, nickname: str):
        print(f'{nickname} logged in!')
        connection.nickname = nickname

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
        game_metadata = {game_id: {
            'name': game.name,
            'creator': game.owner.nickname,
            'board': game.board.name,
            'available_colors': list(map(lambda color: color.value, game.get_available_colors())),
            'total_players': len(game.board.colors),
        } for game_id, game in games.items()}

        await connection.run('update_game_metadata', {
            'game_metadata': game_metadata,
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

        await get_games(connection)

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

        if connection in game.players.values():
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

    ''' Note to Self:
    
    This should work by the user first requesting all available plys (ordered).
    Then the user can send back the index of which ply they are interested in for
    each specific from/to pair.
    '''

    @network.command()
    async def ply_scan(connection: Connection, game_id: str, row: int, col: int):
        pass  # TODO

    @network.command()
    async def get_plies(connection: Connection, game_id: str, from_row: int, from_col: int, to_row: int, to_col: int):
        if game_id not in games:
            await connection.error('Game id does not exist.')
            return

        plies = games[game_id].get_plies((from_row, from_col), (to_row, to_col))
        result = [ply_to_json(ply) for ply in plies]

        await connection.run('plies')
        # TODO: Format and send plies back to client.

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
