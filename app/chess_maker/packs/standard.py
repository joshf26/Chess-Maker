import unittest

from typing import Optional, Dict, Tuple, List, Type

from ..color import Color
from ..testing.mock_network import MockNetwork
from ..board import Board
from ..game import Game
from ..piece import Piece
from ..ply_type import PlyType, MoveAction, DestroyAction


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

    def _ply_types(self, from_row: int, from_col: int, to_row: int, to_col: int):
        return self.game.board.tiles[from_row, from_col].ply_types(from_row, from_col, to_row, to_col, self.game)

    def test_single_advance(self):
        self.assertEqual(
            self._ply_types(6, 0, 5, 0),
            [PlyType([MoveAction(6, 0, 5, 0)])],
            'white pawn cannot single advance to empty space',
        )

        self.assertEqual(
            self._ply_types(1, 0, 2, 0),
            [PlyType([MoveAction(1, 0, 2, 0)])],
            'black pawn cannot single advance to empty space',
        )

    def test_double_advance(self):
        self.assertEqual(
            self._ply_types(6, 0, 4, 0),
            [PlyType([MoveAction(6, 0, 4, 0)])],
            'white pawn cannot double advance to empty space on its first move',
        )

        self.game.board.tiles[6, 0].moves += 1
        self.assertEqual(
            self._ply_types(6, 0, 4, 0),
            [],
            'white pawn can double advance to empty space on its second move',
        )

        self.assertEqual(
            self._ply_types(1, 0, 3, 0),
            [PlyType([MoveAction(1, 0, 3, 0)])],
            'black pawn cannot double advance to empty space on its first move',
        )

        self.game.board.tiles[1, 0].moves += 1
        self.assertEqual(
            self._ply_types(1, 0, 3, 0),
            [],
            'black pawn can double advance to empty space on its second move',
        )

    def test_capture(self):
        # Move the white pawn at (6, 1) to (2, 1).
        self.game.board.tiles[2, 1] = self.game.board.tiles.pop((6, 1))

        self.assertEqual(
            self._ply_types(2, 1, 1, 0),
            [PlyType([DestroyAction(1, 0), MoveAction(2, 1, 1, 0)])],
            'white pawn cannot capture left diagonally',
        )

        self.assertEqual(
            self._ply_types(2, 1, 1, 2),
            [PlyType([DestroyAction(1, 2), MoveAction(2, 1, 1, 2)])],
            'white pawn cannot capture right diagonally',
        )

        # Move the black pawn at (1, 1) to (5, 1).
        self.game.board.tiles[5, 1] = self.game.board.tiles.pop((1, 1))

        self.assertEqual(
            self._ply_types(5, 1, 6, 0),
            [PlyType([DestroyAction(6, 0), MoveAction(5, 1, 6, 0)])],
            'black pawn cannot capture right diagonally',
        )

        self.assertEqual(
            self._ply_types(5, 1, 6, 2),
            [PlyType([DestroyAction(6, 2), MoveAction(5, 1, 6, 2)])],
            'black pawn cannot capture left diagonally',
        )

    def test_en_passant(self):
        # Move the white pawn at (6, 1) to (3, 1).
        self.game.board.tiles[3, 1] = self.game.board.tiles.pop((6, 1))

        # Move the black pawn at (1, 0) to (3, 0).
        self.game.board.tiles[3, 0] = self.game.board.tiles.pop((1, 0))

        # Move the black pawn at (1, 2) to (3, 2).
        self.game.board.tiles[3, 2] = self.game.board.tiles.pop((1, 2))

        print(f'\n{self.game.board}')

        self.assertEqual(
            self._ply_types(3, 1, 2, 0),
            [PlyType([DestroyAction(3, 0), MoveAction(3, 1, 2, 0)])],
            'white pawn cannot en passant left',
        )

        self.assertEqual(
            self._ply_types(3, 1, 2, 2),
            [PlyType([DestroyAction(3, 2), MoveAction(3, 1, 2, 2)])],
            'white pawn cannot en passant right',
        )

        # TODO: Test black en passant.

    def test_illegal_moves(self):
        # Move the white pawn at (6, 0) to (4, 0).
        self.game.board.tiles[4, 0] = self.game.board.tiles.pop((6, 0))

        self.assertEqual(
            self._ply_types(4, 0, 5, 0),
            [],
            'white pawn can single advance backwards',
        )

        # Move the black pawn at (1, 0) to (3, 0).
        self.game.board.tiles[3, 0] = self.game.board.tiles.pop((1, 0))

        self.assertEqual(
            self._ply_types(3, 0, 2, 0),
            [],
            'black pawn can single advance backwards',
        )

        # TODO: Test backwards capturing.


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
