from typing import Dict

from .board import Board
from .color import Color
from .network import Network, Connection


class Game:

    def __init__(self, game_id: str, board: Board, network: Network):
        self.game_id = game_id
        self.board = board
        self.network = network
        self.players: Dict[Color, Connection] = {}

        self.started = False
        self.move = 0
        self.ply = 0

        @self.network.command(game_id)
        async def get_state(connection: Connection):
            await connection.send({
                'Here is': 'Some state!',
            })

    def add_player(self, connection: Connection, color: Color):
        self.players[color] = connection
