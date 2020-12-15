from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable
    from chessmaker import GameData, Ply, Vector2

from chessmaker import NoMovesError, Piece
from ..helpers import capture_or_move_if_empty, axis_direction, ORDINALS, load_image


class Bishop(Piece):
    name = 'Bishop'
    image = load_image('standard', 'images/bishop.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Iterable[Ply]:
        if axis_direction(from_pos, to_pos) not in ORDINALS:
            raise NoMovesError('That piece can only move in ordinals directions.')

        return capture_or_move_if_empty(game_data.board, self.color, from_pos, to_pos)


# TODO: Add unit tests.
