from importlib import import_module
from typing import Dict
from uuid import uuid4

from color import Color
from game import Game
from network import Network, Connection

PORT = 8000


def main():
    network = Network()
    games: Dict[str, Game] = {}

    @network.command()
    async def login(connection: Connection, nickname: str):
        print(f'{nickname} logged in!')
        connection.nickname = nickname

    @network.command()
    async def get_games(connection: Connection):
        game_metadata = {game_id: {
            'name': game.name,
            'creator': game.owner.nickname,
            'board': game.board.name,
            'current_players': len(game.players),
            'total_players': len(game.board.colors),
        } for game_id, game in games.items()}

        await connection.send({
            'command': 'update_game_metadata',
            'parameters': {
                'game_metadata': game_metadata,
            },
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

        game = Game(game_id, name, connection, board_class(), network)
        games[game_id] = game

        await connection.send({
            'game_id': game_id,
        })

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
