import unittest

from typing import Optional, Dict, Tuple, List, Type

from ..color import Color
from ..testing.mock_network import MockNetwork
from ..board import Board
from ..game import Game
from ..piece import Piece
from ..ply_type import PlyType, MoveAction


# Pieces


class Pawn(Piece):
    image = ''

    def ply_types(
        self,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        game: Game,
    ) -> List[PlyType]:
        result: List[PlyType] = []

        # Check if the offset is forward to a free space.
        if to_col == from_col and (to_row, to_col) not in game.board.tiles:
            forward_offset = to_row - from_row

            # Check for single or double advance.
            if (
                (self.color == Color.WHITE and (forward_offset == -1 or (self.moves == 0 and forward_offset == -2))) or
                (self.color == Color.BLACK and (forward_offset == 1 or (self.moves == 0 and forward_offset == 2)))
            ):
                result.append(PlyType([MoveAction(from_row, from_col, to_row, to_col)]))

            # TODO: Check for en passant.

        # TODO: Check for diagonal attack.

        return result


class TestPawn(unittest.TestCase):

    def setUp(self):
        self.game = Game('test', Standard8x8(), MockNetwork())
        print(self.game.board)

    def test_single_advance(self):
        # Make sure the white pawn can advance forward.
        self.assertEqual(
            self.game.board.tiles[6, 0].ply_types(6, 0, 5, 0, self.game),
            [PlyType([MoveAction(6, 0, 5, 0)])]
        )


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


# Boards


class Standard8x8(Board):
    size = (8, 8)

    colors = {
        Color.WHITE,
        Color.BLACK,
    }

    def init_board(self) -> Dict[Tuple[int, int], Piece]:
        board: Dict[Tuple[int, int], Piece] = {}

        for color, row in zip([Color.WHITE, Color.BLACK], [7, 0]):
            board[row, 0] = Rook(color)
            board[row, 1] = Knight(color)
            board[row, 2] = Bishop(color)
            board[row, 3] = Queen(color)
            board[row, 4] = King(color)
            board[row, 5] = Bishop(color)
            board[row, 6] = Knight(color)
            board[row, 7] = Rook(color)

        for color, row in zip([Color.WHITE, Color.BLACK], [6, 1]):
            for col in range(8):
                board[row, col] = Pawn(color)

        return board

    def ply_types(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        color: Color,
        piece: Piece,
    ) -> List[Type[PlyType]]:
        result: List[Type[PlyType]] = []

        return result

    def upgrade(self, x: int, y: int, color: Color, piece: Piece) -> Optional[Piece]:
        if isinstance(piece, Pawn):
            return

        if (color == Color.WHITE and y == 0) or (color == Color.BLACK and y == 7):
            return Queen(color)


if __name__ == '__main__':
    unittest.main()
