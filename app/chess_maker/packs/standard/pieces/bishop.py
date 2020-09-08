from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from packs.standard.helpers import capture_or_move_if_empty, axis_direction, ORDINALS
from piece import Piece
from pack_util import load_image
from ply import Ply

if TYPE_CHECKING:
    from game import GameData
    from vector2 import Vector2


class Bishop(Piece):
    name = 'Bishop'
    image = load_image('standard', 'images/bishop.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Iterable[Ply]:
        if axis_direction(from_pos, to_pos) not in ORDINALS:
            return ()

        return capture_or_move_if_empty(game_data.board, self.color, from_pos, to_pos)


# TODO: Add unit tests.
