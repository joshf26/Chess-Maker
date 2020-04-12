from __future__ import annotations
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from chess_maker.ply_type import PlyType
    from chess_maker.color import Color
    from chess_maker.game import Game


class Piece:

    def __init__(self, color: Color):
        self.color = color
        self.moves = 0

    def ply_types(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        game: Game,
    ) -> Set[PlyType]:
        raise NotImplementedError
