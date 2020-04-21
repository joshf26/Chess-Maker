from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .ply import Ply
    from .color import Color
    from .network import Network, Connection
    from .board import Board, Tiles


class Game:

    def __init__(self, game_id: str, board: Board, network: Network):
        self.game_id = game_id
        self.board = board
        self.network = network
        self.players: Dict[Color, Connection] = {}

        self.started = False
        self.plies: List[Ply] = []
        self.history: List[Tiles] = []

        @self.network.command(game_id)
        async def get_state(connection: Connection):
            await connection.send({
                'Here is': 'Some state!',
            })

    def add_player(self, connection: Connection, color: Color):
        self.players[color] = connection
