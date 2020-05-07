from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from piece import Piece, load_image
from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from game import Game


class Bishop(Piece):
    name = 'Bishop'
    image = load_image('standard', 'images/bishop.svg')

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        row_diff = to_pos[0] - from_pos[0]
        col_diff = to_pos[1] - from_pos[1]

        # Make sure the bishop is moving along a diagonal.
        if to_pos == from_pos or abs(row_diff) != abs(col_diff):
            return []

        # Check for collisions.
        if any((
            from_pos[0] + (offset if row_diff > 0 else -offset),
            from_pos[1] + (offset if col_diff > 0 else -offset)
        ) in game.board.tiles for offset in range(1, abs(row_diff))):
            return []

        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [[DestroyAction(to_pos), MoveAction(from_pos, to_pos)]]
        else:
            return [[MoveAction(from_pos, to_pos)]]

        return []


# TODO: Add unit tests.
