from importlib import import_module
from uuid import uuid4

from game import Game
from network import Network, ReplyCallable, ErrorCallable

PORT = 8000


def main():
    network = Network()
    games = {}

    @network.command
    async def create_game(reply: ReplyCallable, error: ErrorCallable, pack: str, board: str):
        try:
            pack = import_module(f'packs.{pack}')
        except ModuleNotFoundError:
            await error(f'Package "{pack}" does not exist.')
            return

        try:
            board_class = getattr(pack, board)
        except AttributeError:
            await error(f'Board {board} does not exist in package {pack}.')
            return

        while (game_id := str(uuid4())) in games:
            pass

        game = Game(board_class(), network)
        games[game_id] = game

        await reply({
            'game_id': game_id,
        })

    network.serve(8000)


if __name__ == '__main__':
    main()
