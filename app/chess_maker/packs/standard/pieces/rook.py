from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from packs.standard.pieces.knight import signed_range
from piece import Piece, load_image
from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from game import Game


class Rook(Piece):
    name = 'Rook'
    image = load_image('standard', 'images/rook.svg')

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        # Make sure the rook is moving alone the same axis.
        if to_pos == from_pos or (to_pos[0] != from_pos[0] and to_pos[1] != from_pos[1]):
            return []

        # Check for collisions.
        if to_pos[0] != from_pos[0]:
            if any((row, to_pos[1]) in game.board.tiles for row in signed_range(from_pos[0], to_pos[0])):
                return []
        else:
            if any((to_pos[0], col) in game.board.tiles for col in signed_range(from_pos[1], to_pos[1])):
                return []

        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [[DestroyAction(to_pos), MoveAction(from_pos, to_pos)]]
        else:
            return [[MoveAction(from_pos, to_pos)]]

        return []


# TODO: Add unit tests.
