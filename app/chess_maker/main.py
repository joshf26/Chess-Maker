from typing import Dict
from uuid import uuid4

from color import Color
from game import Game
from network import Network, Connection
from pack import load_packs
from ply import ply_to_json

PORT = 8000


def main():
    games: Dict[str, Game] = {}
    packs = load_packs()

    async def on_disconnect(connection: Connection):
        change_made = False
        for game in games.values():
            if connection in game.subscribers:
                game.subscribers.remove(connection)
                change_made = True

            if connection in game.players:
                game.players.remove_connection(connection)
                change_made = True

        if change_made:
            await send_metadata_update_to_all()

    network = Network(on_disconnect)

    def make_game_metadata(connection: Connection) -> dict:
        return {game_id: {
            'name': game.name,
            'creator': game.owner.nickname,
            'pack': game.board.__module__.split('.')[1],
            'board': game.board.name,
            'available_colors': list(map(lambda color: color.value, game.get_available_colors())),
            'total_players': len(game.board.colors),
            'playing_as': None if (color := game.players.get_color(connection)) is None else color.value,
        } for game_id, game in games.items()}

    async def send_metadata_update_to_all():
        for connection in network.connections:
            await connection.run('update_game_metadata', {
                'game_metadata': make_game_metadata(connection),
            })

    @network.command()
    async def login(connection: Connection, nickname: str):
        nicknames = {connection.nickname for connection in network.connections}
        while nickname in nicknames:
            nickname += ' 2'

        print(f'{nickname} logged in!')
        connection.nickname = nickname

        await connection.run('set_nickname', {'nickname': nickname})
        await send_pack_data(connection)

    @network.command()
    async def send_pack_data(connection: Connection):
        pack_data: Dict[str, dict] = {}

        for pack, (boards, pieces) in packs.items():
            pack_data[pack] = {
                'pieces': {piece.name: {
                    'image': piece.image,
                } for piece in pieces},

                'boards': {board.name: {
                    'rows': board.size[1],
                    'cols': board.size[0],
                } for board in boards},
            }

        await connection.run('update_pack_data', {
            'pack_data': pack_data,
        })

    @network.command()
    async def get_games(connection: Connection):
        await connection.run('update_game_metadata', {
            'game_metadata': make_game_metadata(connection),
        })

    @network.command()
    async def create_game(connection: Connection, name: str, pack: str, board: str):
        if pack not in packs:
            await connection.error('Package does not exist.')
            return

        board_class = next(filter(lambda b: b.name == board, packs[pack][0]), None)

        if board_class is None:
            await connection.error('Board does not exist.')
            return

        game = Game(name, connection, board_class, network)
        games[game.id] = game

        await connection.send({
            'game_id': game.id,
        })

        await send_metadata_update_to_all()

    @network.command()
    async def delete_game(connection: Connection, game_id: str):
        if game_id not in games:
            await connection.error('Game does not exist.')
            return

        game = games[game_id]

        if game.owner.nickname != connection.nickname:
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
        game.subscribers.add(connection)

        game_data = game.get_full_data(connection)
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
            await game.send_update_to_subscribers()
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

    @network.command()
    async def click_button(connection: Connection, game_id: str, button_id: str):
        if game_id not in games:
            await connection.error('Game id does not exist.')
            return

        game = games[game_id]
        await game.click_button(connection, button_id)

    network.serve(PORT)


if __name__ == '__main__':
    main()
