from importlib import import_module
from typing import Dict
from uuid import uuid4

from color import Color
from game import Game
from network import Network, Connection
from pack import load_packs

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
            'current_players': len(game.players),
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

        await connection.send({})

    network.serve(8000)


if __name__ == '__main__':
    main()
