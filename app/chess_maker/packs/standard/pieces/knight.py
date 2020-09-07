from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from packs.standard.helpers import capture_or_move
from piece import Piece
from pack_util import load_image
from ply import Ply

if TYPE_CHECKING:
    from game import GameData
    from vector2 import Vector2


class Knight(Piece):
    name = 'Knight'
    image = load_image('standard', 'images/knight.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Iterable[Ply]:
        row_dist = abs(to_pos.row - from_pos.row)
        col_dist = abs(to_pos.col - from_pos.col)

        # Check for valid knight move.
        if (row_dist == 2 and col_dist == 1) or (row_dist == 1 and col_dist == 2):
            yield from capture_or_move(game_data.board, self.color, from_pos, to_pos)


# TODO: Add unit tests.
