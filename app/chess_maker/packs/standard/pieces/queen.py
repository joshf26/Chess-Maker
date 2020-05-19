from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from packs.standard.helpers import capture_or_move_if_empty
from piece import Piece, load_image
from ply import Ply

if TYPE_CHECKING:
    from game import Game
    from board import Vector2


class Queen(Piece):
    name = 'Queen'
    image = load_image('standard', 'images/queen.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> Generator[Ply]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # Make sure the queen is moving like either a rook or bishop.
        invalid_bishop = abs(row_diff) != abs(col_diff)
        invalid_rook = (to_pos.row != from_pos.row and to_pos.col != from_pos.col)
        if to_pos == from_pos or (invalid_rook and invalid_bishop):
            return

        yield from capture_or_move_if_empty(game.board, self.color, from_pos, to_pos)


# TODO: Add unit tests.
