from typing import Dict, Tuple

from board import Board
from color import Color
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Piece, Direction


class Standard8x8(Board):
    name = 'Standard 8x8'
    size = (8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self) -> Dict[Tuple[int, int], Piece]:
        board: Dict[Tuple[int, int], Piece] = {}

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
