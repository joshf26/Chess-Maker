import unittest
from typing import Tuple

from packs.standard.boards.standard8x8 import Standard8x8
from ply import MoveAction, DestroyAction
from testing import make_test_game


class TestPawn(unittest.TestCase):
    # TODO: Test directions other than North and South.

    def setUp(self):
        self.game = make_test_game(Standard8x8())

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

    def test_white_en_passant(self):
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

    def test_black_en_passant(self):
        # Move the white pawn at (6, 3) to (5, 3). This move is only here to switch the current turn to black.
        self.game.apply_ply([MoveAction((6, 3), (5, 3))])

        # Move the black pawn at (1, 1) to (4, 1).
        self.game.apply_ply([MoveAction((1, 1), (4, 1))])

        # Move the white pawn at (6, 0) to (4, 0).
        self.game.apply_ply([MoveAction((6, 0), (4, 0))])

        self.assertEqual(
            self._ply_types((4, 1), (5, 0)),
            [[DestroyAction((4, 0)), MoveAction((4, 1), (5, 0))]],
            'black pawn cannot en passant right',
        )

        # Move the black pawn at (1, 6) to (4, 6).
        self.game.apply_ply([MoveAction((1, 6), (4, 6))])

        # Move the white pawn at (6, 7) to (4, 7).
        self.game.apply_ply([MoveAction((6, 7), (4, 7))])

        print(f'\n\n{self.game.board}\n\n')

        self.assertEqual(
            self._ply_types((4, 6), (5, 7)),
            [[DestroyAction((4, 7)), MoveAction((4, 6), (5, 7))]],
            'black pawn cannot en passant left',
        )

    def test_illegal_moves(self):
        # Move the white pawn at (6, 0) to (4, 0).
        self.game.apply_ply([MoveAction((6, 0), (4, 0))])

        self.assertEqual(
            self._ply_types((4, 0), (5, 0)),
            [],
            'white pawn can single advance backwards',
        )

        # Move the black pawn at (1, 0) to (3, 0).
        self.game.apply_ply([MoveAction((1, 0), (3, 0))])

        self.assertEqual(
            self._ply_types((3, 0), (2, 0)),
            [],
            'black pawn can single advance backwards',
        )

        # TODO: Test backwards capturing.
        # TODO: Test own color capturing.
