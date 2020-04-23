from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from .color import Color
    from .network import Network, Connection
    from .board import Board, Tiles


@dataclass
class HistoryEvent:
    color: Color
    tiles: Tiles
    ply: Ply


class Game:

    def __init__(self, game_id: str, name: str, owner: Connection, board: Board, network: Network):
        self.name = name
        self.owner = owner
        self.board = board
        self.network = network
        self.players: Dict[Color, Connection] = {}

        self.plies: List[Ply] = []
        self.history: List[HistoryEvent] = []

        @self.network.command(game_id)
        async def get_state(connection: Connection):
            await connection.send({
                'Here is': 'Some state!',
            })

    def apply_ply(self, ply: Ply):
        self.history.append(HistoryEvent(self.current_color(), self.board.tiles.copy(), ply))

        for action in ply:
            if isinstance(action, MoveAction):
                self.board.tiles[action.from_pos].moves += 1
                self.board.tiles[action.to_pos] = self.board.tiles.pop(action.from_pos)

            if isinstance(action, DestroyAction):
                self.board.tiles.pop(action.pos)

    def add_player(self, connection: Connection, color: Color):
        self.players[color] = connection

    def current_color(self) -> Color:
        if len(self.history) == 0:
            # TODO: Board should be validated at some point to ensure there is at least one color.
            return self.board.colors[0]

        color_index = self.board.colors.index(self.history[-1].color) + 1
        return self.board.colors[color_index % len(self.board.colors)]

    def n_event_by_color(self, color: Color, n: int, reverse: bool = False) -> Optional[HistoryEvent]:
        assert n > 0, 'n must be greater than 0'

        counter = 0
        for history_event in reversed(self.history) if reverse else self.history:
            if history_event.color == color:
                counter += 1
                if counter == n:
                    return history_event

        return None
