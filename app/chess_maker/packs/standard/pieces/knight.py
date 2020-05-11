from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from piece import Piece, load_image
from ply import Ply, DestroyAction, MoveAction

if TYPE_CHECKING:
    from game import Game


class Knight(Piece):
    name = 'Knight'
    image = load_image('standard', 'images/knight.svg')

    def ply_types(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], game: Game) -> List[Tuple[str, Ply]]:
        row_dist = abs(to_pos[0] - from_pos[0])
        col_dist = abs(to_pos[1] - from_pos[1])

        # Check for valid knight move.
        if (row_dist == 2 and col_dist == 1) or (row_dist == 1 and col_dist == 2):
            # Check for capture.
            if to_pos in game.board.tiles:
                if game.board.tiles[to_pos].color != self.color:
                    return [('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])]
            else:
                return [('Move', [MoveAction(from_pos, to_pos)])]

        return []


# TODO: Add unit tests.
