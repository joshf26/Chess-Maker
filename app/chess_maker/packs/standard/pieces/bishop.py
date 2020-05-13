from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from piece import Piece, load_image
from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from game import Game
    from board import Vector2


class Bishop(Piece):
    name = 'Bishop'
    image = load_image('standard', 'images/bishop.svg')

    def ply_types(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> List[Tuple[str, Ply]]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # Make sure the bishop is moving along a diagonal.
        if to_pos == from_pos or abs(row_diff) != abs(col_diff):
            return []

        # Check for collisions.
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
