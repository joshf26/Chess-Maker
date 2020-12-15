from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Generator

from chessmaker import GameData, Direction, Piece, Ply, Vector2
from ....packs.standard.helpers import load_image
from .king import King


class Man(Piece):
    name = 'Man'
    image = load_image('checkers', 'images/man.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        row_diff = to_pos.row - from_pos.row

        if (self.direction == Direction.NORTH and row_diff > 0) or (self.direction == Direction.SOUTH and row_diff < 0):
            return

        yield from King.move_or_capture(from_pos, to_pos, game_data)
