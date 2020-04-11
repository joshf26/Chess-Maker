from typing import Optional, Dict, Tuple

from board import Board
from game import Color
from piece import Piece


# Boards


class Standard8x8(Board):
    colors = {
        Color.WHITE,
        Color.BLACK
    }

    def init_board(self) -> Dict[Tuple[int, int], Piece]:
        board: Dict[Tuple[int, int], Piece] = {}

        for color, row in zip([Color.WHITE, Color.BLACK], [7, 0]):
            board[0, row] = Rook(color)
            board[7, row] = Rook(color)
            board[1, row] = Knight(color)
            board[6, row] = Knight(color)
            board[2, row] = Bishop(color)
            board[5, row] = Bishop(color)
            board[3, row] = Queen(color)
            board[4, row] = King(color)

        for col in range(8):
            for player, row in zip([Color.WHITE, Color.BLACK], [6, 1]):
                board[col, row] = Pawn(player)

        return board

    def space_valid(self, x: int, y: int, color: Color, piece: Piece) -> bool:
        return 0 <= x <= 8 and 0 <= y <= 8

    def upgrade(self, x: int, y: int, color: Color, piece: Piece) -> Optional[Piece]:
        if isinstance(piece, Pawn):
            return

        if (color == Color.WHITE and y == 0) or (color == Color.BLACK and y == 7):
            return Queen(color)


# Pieces


class Pawn(Piece):
    pass


class Rook(Piece):
    pass


class Knight(Piece):
    pass


class Bishop(Piece):
    pass


class Queen(Piece):
    pass


class King(Piece):
    pass
