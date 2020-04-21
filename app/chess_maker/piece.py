from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Set, Tuple

if TYPE_CHECKING:
    from chess_maker.ply import Ply
    from chess_maker.color import Color
    from chess_maker.game import Game


class Direction(Enum):
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7


class Piece:

    def __init__(self, color: Color, direction: Direction):
        self.color = color
        self.direction = direction

        self.moves = 0

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> Set[Ply]:
        raise NotImplementedError
