from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set, Tuple, Dict

from ply import Ply, MoveAction, DestroyAction
from color import Color

if TYPE_CHECKING:
    from network import Network, Connection
    from board import Board, Tiles


@dataclass
class HistoryEvent:
    color: Color
    tiles: Tiles
    ply: Ply


class ColorConnections:

    def __init__(self):
        self.color_to_connection: Dict[Color, Connection] = {}
        self.connection_to_color: Dict[Connection, Color] = {}

    def __len__(self):
        return len(self.color_to_connection)

    def __contains__(self, item):
        if isinstance(item, Color):
            return item in self.color_to_connection
        else:
            return item in self.connection_to_color

    def set(self, color: Color, connection: Connection):
        self.color_to_connection[color] = connection
        self.connection_to_color[connection] = color

    def remove_connection(self, connection: Connection):
        color = self.connection_to_color[connection]

        del self.connection_to_color[connection]
        del self.color_to_connection[color]

    def get_color(self, connection: Connection):
        return self.connection_to_color.get(connection, None)

    def get_connection(self, color: Color):
        return self.color_to_connection.get(color, None)


class Game:

    def __init__(self, name: str, owner: Connection, board: Board, network: Network):
        self.name = name
        self.owner = owner
        self.board = board
        self.network = network

        self.subscribers: Set[Connection] = set()
        self.players = ColorConnections()

        self.plies: List[Ply] = []
        self.history: List[HistoryEvent] = []

    def get_available_colors(self) -> Set[Color]:
        colors = set(self.board.colors.copy())
        taken_colors = set(self.players.color_to_connection.keys())

        return colors - taken_colors

    def get_full_data(self) -> dict:
        # TODO: Maybe make this nested dictionaries instead of strings.
        return {
            'tiles': [{
                'row': position[0],
                'col': position[1],
                'pack': piece.__module__.split('.')[1],  # TODO: Extract into function?
                'piece': piece.__class__.__name__,
                'color': piece.color.value,
                'direction': piece.direction.value,
            } for position, piece in self.board.tiles.items()]
        }

    # TODO: Make this a generator.
    def get_plies(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> List[Ply]:
        piece_plies = self.board.tiles[from_pos].ply_types(from_pos, to_pos, self)

        return self.board.process_plies(piece_plies, from_pos, to_pos, self)

    def apply_ply(self, ply: Ply):
        self.history.append(HistoryEvent(self.current_color(), self.board.tiles.copy(), ply))

        for action in ply:
            if isinstance(action, MoveAction):
                self.board.tiles[action.from_pos].moves += 1
                self.board.tiles[action.to_pos] = self.board.tiles.pop(action.from_pos)

            if isinstance(action, DestroyAction):
                self.board.tiles.pop(action.pos)

    def add_player(self, connection: Connection, color: Color):
        self.players.set(color, connection)

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
