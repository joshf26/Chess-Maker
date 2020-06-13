from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from packs.standard.helpers import axis_direction, closest_piece_along_direction, OFFSETS, capture_or_move
from packs.standard.pieces.rook import Rook
from piece import Piece
from pack_util import load_image
from ply import Ply, DestroyAction, MoveAction

if TYPE_CHECKING:
    from game import GameData
    from vector2 import Vector2


class King(Piece):
    name = 'King'
    image = load_image('standard', 'images/king.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        row_dist = abs(to_pos.row - from_pos.row)
        col_dist = abs(to_pos.col - from_pos.col)

        # Make sure the king is moving one square.
        if from_pos == to_pos or row_dist > 1 or col_dist > 1:
            # Check for castling.
            if not (
                (row_dist == 2 and col_dist == 0)
                or (row_dist == 0 and col_dist == 2)
                or row_dist == col_dist == 2
            ):
                return

            direction = axis_direction(from_pos, to_pos)
            if self.moves > 0 or direction is None:
                return

            piece_data = closest_piece_along_direction(game_data, from_pos, direction)
            if piece_data is None:
                return

            piece, position = piece_data

            if not isinstance(piece, Rook) or piece.moves > 0:
                return

            yield Ply('Castle', [MoveAction(from_pos, to_pos), MoveAction(position, from_pos + OFFSETS[direction])])

        else:
            yield from capture_or_move(game_data.board, self.color, from_pos, to_pos)
