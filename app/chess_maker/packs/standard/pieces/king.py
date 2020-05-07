from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from piece import Piece, load_image
from ply import Ply, DestroyAction, MoveAction

if TYPE_CHECKING:
    from game import Game


class King(Piece):
    name = 'King'
    image = load_image('standard', 'images/king.svg')

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        row_dist = abs(to_pos[0] - from_pos[0])
        col_dist = abs(to_pos[1] - from_pos[1])

        # Make sure the king is moving one square.
        if from_pos == to_pos or row_dist > 1 or col_dist > 1:
            return []

        # Check for capture.
        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [[DestroyAction(to_pos), MoveAction(from_pos, to_pos)]]
        else:
            return [[MoveAction(from_pos, to_pos)]]

        return []
