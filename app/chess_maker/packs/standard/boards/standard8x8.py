from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from board import Board
from color import Color
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Direction

if TYPE_CHECKING:
    from ply import Ply
    from game import Game
    from board import Tiles


class Standard8x8(Board):
    name = 'Standard 8x8'
    size = (8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self) -> Tiles:
        board: Tiles = {}

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board[row, 0] = Rook(color, direction)
            board[row, 1] = Knight(color, direction)
            board[row, 2] = Bishop(color, direction)
            board[row, 3] = Queen(color, direction)
            board[row, 4] = King(color, direction)
            board[row, 5] = Bishop(color, direction)
            board[row, 6] = Knight(color, direction)
            board[row, 7] = Rook(color, direction)

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                board[row, col] = Pawn(color, direction)

        return board

    def process_plies(
        self,
        plies: List[Ply],
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> List[Ply]:
        if self.tiles[from_pos].color == self.game.current_color():
            return plies

        return []
