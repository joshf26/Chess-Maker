import unittest

from typing import Optional, Dict, Tuple, List, Type

from ..color import Color
from ..testing.mock_network import MockNetwork
from ..board import Board
from ..game import Game
from ..piece import Piece, Direction
from ..ply import Ply, MoveAction, DestroyAction


# Pieces


class Pawn(Piece):
    image = ''

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        result: List[Ply] = []

        row_diff = to_pos[0] - from_pos[0]
        col_diff = to_pos[1] - from_pos[1]

        if self.direction == Direction.NORTH:
            if to_pos not in game.board.tiles:
                # Check for single or double advance.
                if col_diff == 0 and (row_diff == -1 or (self.moves == 0 and row_diff == -2)):
                    result.append([MoveAction(from_pos, to_pos)])

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = to_pos[0] + 1, to_pos[1]
                    if (
                        captured_pawn_pos in game.board.tiles and
                        isinstance(game.board.tiles[captured_pawn_pos], Pawn) and
                        game.board.tiles[captured_pawn_pos].color != self.color
                    ):
                        event = game.n_event_by_color(game.board.tiles[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            event.ply == [MoveAction((to_pos[0] - 1, to_pos[1]), captured_pawn_pos)]
                        ):
                            result.append([DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)])

            # Check for diagonal capture.
            # TODO: Add test for own color capture.
            elif row_diff == -1 and abs(col_diff) == 1 and game.board.tiles[to_pos].color != self.color:
                result.append([DestroyAction(to_pos), MoveAction(from_pos, to_pos)])

        return result


class TestPawn(unittest.TestCase):

    def setUp(self):
        self.game = Game('test', Standard8x8(), MockNetwork())

    def _ply_types(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        return self.game.board.tiles[from_pos].ply_types(from_pos, to_pos, self.game)

    def test_single_advance(self):
        self.assertEqual(
            self._ply_types((6, 0), (5, 0)),
            [[MoveAction((6, 0), (5, 0))]],
            'white pawn cannot single advance to empty space',
        )

        self.assertEqual(
            self._ply_types((1, 0), (2, 0)),
            [[MoveAction((1, 0), (2, 0))]],
            'black pawn cannot single advance to empty space',
        )

    def test_double_advance(self):
        self.assertEqual(
            self._ply_types((6, 0), (4, 0)),
            [[MoveAction((6, 0), (4, 0))]],
            'white pawn cannot double advance to empty space on its first move',
        )

        self.game.board.tiles[6, 0].moves += 1
        self.assertEqual(
            self._ply_types((6, 0), (4, 0)),
            [],
            'white pawn can double advance to empty space on its second move',
        )

        self.assertEqual(
            self._ply_types((1, 0), (3, 0)),
            [[MoveAction((1, 0), (3, 0))]],
            'black pawn cannot double advance to empty space on its first move',
        )

        self.game.board.tiles[1, 0].moves += 1
        self.assertEqual(
            self._ply_types((1, 0), (3, 0)),
            [],
            'black pawn can double advance to empty space on its second move',
        )

    def test_capture(self):
        # Move the white pawn at (6, 1) to (2, 1).
        self.game.apply_ply([MoveAction((6, 1), (2, 1))])

        self.assertEqual(
            self._ply_types((2, 1), (1, 0)),
            [[DestroyAction((1, 0)), MoveAction((2, 1), (1, 0))]],
            'white pawn cannot capture left diagonally',
        )

        self.assertEqual(
            self._ply_types((2, 1), (1, 2)),
            [[DestroyAction((1, 2)), MoveAction((2, 1), (1, 2))]],
            'white pawn cannot capture right diagonally',
        )

        # Move the black pawn at (1, 1) to (5, 1).
        self.game.apply_ply([MoveAction((1, 1), (5, 1))])

        self.assertEqual(
            self._ply_types((5, 1), (6, 0)),
            [[DestroyAction((6, 0)), MoveAction((5, 1), (6, 0))]],
            'black pawn cannot capture right diagonally',
        )

        self.assertEqual(
            self._ply_types((5, 1), (6, 2)),
            [[DestroyAction((6, 2)), MoveAction((5, 1), (6, 2))]],
            'black pawn cannot capture left diagonally',
        )

    def test_en_passant(self):
        # Move the white pawn at (6, 1) to (3, 1).
        self.game.apply_ply([MoveAction((6, 1), (3, 1))])

        # Move the black pawn at (1, 0) to (3, 0).
        self.game.apply_ply([MoveAction((1, 0), (3, 0))])

        self.assertEqual(
            self._ply_types((3, 1), (2, 0)),
            [[DestroyAction((3, 0)), MoveAction((3, 1), (2, 0))]],
            'white pawn cannot en passant left',
        )

        # Move the white pawn at (6, 6) to (3, 6).
        self.game.apply_ply([MoveAction((6, 6), (3, 6))])

        # Move the black pawn at (1, 7) to (3, 7).
        self.game.apply_ply([MoveAction((1, 7), (3, 7))])

        self.assertEqual(
            self._ply_types((3, 6), (2, 7)),
            [[DestroyAction((3, 7)), MoveAction((3, 6), (2, 7))]],
            'white pawn cannot en passant right',
        )

        # TODO: Test black en passant.

    def test_illegal_moves(self):
        # Move the white pawn at (6, 0) to (4, 0).
        self.game.board.tiles[4, 0] = self.game.board.tiles.pop((6, 0))

        self.assertEqual(
            self._ply_types((4, 0), (5, 0)),
            [],
            'white pawn can single advance backwards',
        )

        # Move the black pawn at (1, 0) to (3, 0).
        self.game.board.tiles[3, 0] = self.game.board.tiles.pop((1, 0))

        self.assertEqual(
            self._ply_types((3, 0), (2, 0)),
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

    def ply_types(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        color: Color,
        piece: Piece,
    ) -> List[Type[Ply]]:
        result: List[Type[Ply]] = []

        return result

    def upgrade(self, x: int, y: int, color: Color, piece: Piece) -> Optional[Piece]:
        if isinstance(piece, Pawn):
            return

        if color == Color.WHITE and y == 0 or (color == Color.BLACK and y == 7):
            return Queen(color, piece.direction)


if __name__ == '__main__':
    unittest.main()
