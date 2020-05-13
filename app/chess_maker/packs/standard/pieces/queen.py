from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from packs.standard.helpers import bidirectional_exclusive_range
from piece import Piece, load_image
from ply import Ply, DestroyAction, MoveAction

if TYPE_CHECKING:
    from game import Game
    from board import Vector2


class Queen(Piece):
    name = 'Queen'
    image = load_image('standard', 'images/queen.svg')

    def ply_types(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> List[Tuple[str, Ply]]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # Make sure the queen is moving like either a rook or bishop.
        invalid_bishop = abs(row_diff) != abs(col_diff)
        invalid_rook = (to_pos.row != from_pos.row and to_pos.col != from_pos.col)
        if to_pos == from_pos or (invalid_rook and invalid_bishop):
            return []

        # Check for collisions.
        if invalid_bishop:
            # Queen is moving like a rook.
            if to_pos.row != from_pos.row:
                if any((row, to_pos.col) in game.board.tiles for row in bidirectional_exclusive_range(from_pos.row, to_pos.row)):
                    return []
            else:
                if any((to_pos.row, col) in game.board.tiles for col in bidirectional_exclusive_range(from_pos.col, to_pos.col)):
                    return []
        else:
            # Queen is moving like a bishop.
            if any((
                from_pos.row + (offset if row_diff > 0 else -offset),
                from_pos.col + (offset if col_diff > 0 else -offset)
            ) in game.board.tiles for offset in range(1, abs(row_diff))):
                return []

        # Check for capture.
        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])]
        else:
            return [('Move', [MoveAction(from_pos, to_pos)])]

        return []


# TODO: Add unit tests.
