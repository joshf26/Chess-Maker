from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from packs.standard.helpers import bidirectional_exclusive_range
from piece import Piece, load_image
from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from game import Game
    from board import Vector2


class Rook(Piece):
    name = 'Rook'
    image = load_image('standard', 'images/rook.svg')

    def ply_types(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> List[Tuple[str, Ply]]:
        # Make sure the rook is moving along the same axis.
        if to_pos == from_pos or (to_pos.row != from_pos.row and to_pos.col != from_pos.col):
            return []

        # Check for collisions. TODO: Extract this and bishop code for queen to use.
        if to_pos.row != from_pos.row:
            if any((row, to_pos.col) in game.board.tiles for row in bidirectional_exclusive_range(from_pos.row, to_pos.row)):
                return []
        else:
            if any((to_pos.row, col) in game.board.tiles for col in bidirectional_exclusive_range(from_pos.col, to_pos.col)):
                return []

        # Check for capture.
        if to_pos in game.board.tiles:
            if game.board.tiles[to_pos].color != self.color:
                return [('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])]
        else:
            return [('Move', [MoveAction(from_pos, to_pos)])]

        return []


# TODO: Add unit tests.
