from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable
    from chessmaker import GameData, Ply, Vector2

from chessmaker import NoMovesError, Piece
from ..helpers import capture_or_move, load_image


class Knight(Piece):
    name = 'Knight'
    image = load_image('standard', 'images/knight.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Iterable[Ply]:
        row_dist = abs(to_pos.row - from_pos.row)
        col_dist = abs(to_pos.col - from_pos.col)

        # Check for valid knight move.
        if (row_dist == 2 and col_dist == 1) or (row_dist == 1 and col_dist == 2):
            return capture_or_move(game_data.board, self.color, from_pos, to_pos)
        else:
            raise NoMovesError('That piece must move two spaces in one cardinal axis, and one in another.')


# TODO: Add unit tests.
