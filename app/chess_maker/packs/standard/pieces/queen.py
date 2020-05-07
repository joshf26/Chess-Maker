from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from packs.standard.pieces.knight import signed_range
from piece import Piece, load_image
from ply import Ply, DestroyAction, MoveAction

if TYPE_CHECKING:
    from game import Game


class Queen(Piece):
    name = 'Queen'
    image = load_image('standard', 'images/queen.svg')

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        row_diff = to_pos[0] - from_pos[0]
        col_diff = to_pos[1] - from_pos[1]

        # Make sure the queen is moving like either a rook or bishop.
        invalid_bishop = abs(row_diff) != abs(col_diff)
        invalid_rook = (to_pos[0] != from_pos[0] and to_pos[1] != from_pos[1])
        if to_pos == from_pos or (invalid_rook and invalid_bishop):
            return []

        # Check for collisions.
        if invalid_bishop:
            # Queen is moving like a rook.
            if to_pos[0] != from_pos[0]:
                if any((row, to_pos[1]) in game.board.tiles for row in signed_range(from_pos[0], to_pos[0])):
                    return []
            else:
                if any((to_pos[0], col) in game.board.tiles for col in signed_range(from_pos[1], to_pos[1])):
                    return []
        else:
            # Queen is moving like a bishop.
            if any((
                from_pos[0] + (offset if row_diff > 0 else -offset),
                from_pos[1] + (offset if col_diff > 0 else -offset)
            ) in game.board.tiles for offset in range(1, abs(row_diff))):
                return []

        # Check for capture.
        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [[DestroyAction(to_pos), MoveAction(from_pos, to_pos)]]
        else:
            return [[MoveAction(from_pos, to_pos)]]

        return []


# TODO: Add unit tests.
