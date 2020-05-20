from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from packs.standard.helpers import capture_or_move_if_empty
from piece import Piece, load_image
from ply import Ply

if TYPE_CHECKING:
    from game import GameData
    from vector2 import Vector2


class Rook(Piece):
    name = 'Rook'
    image = load_image('standard', 'images/rook.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        # Make sure the rook is moving along the same axis.
        if to_pos == from_pos or (to_pos.row != from_pos.row and to_pos.col != from_pos.col):
            return

        yield from capture_or_move_if_empty(game_data.board, self.color, from_pos, to_pos)


# TODO: Add unit tests.
