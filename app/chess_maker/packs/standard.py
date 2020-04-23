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
    # Adapted from https://commons.wikimedia.org/wiki/File:Chess_plt45.svg
    image = 'M 14.89117,56.08699 C 11.46071,47.90636 16.65938,39.07576 23.26772,34.70099 L 24.28728,34.14673 L 23.68251,33.58519 C 19.26818,28.27655 20.68869,21.26738 26.73105,18.14756 C 25.62163,16.32124 25.2643,14.46735 25.67416,12.34281 C 26.53639,9.202264 29.18769,8.055069 32.04438,7.803115 C 34.97685,7.922921 37.25664,9.437134 38.27278,12.34281 C 38.92038,14.47122 38.13045,16.30259 37.21588,18.14756 C 43.91553,21.29693 43.91305,28.01263 40.26441,33.58519 L 39.65965,34.14673 C 46.6426,37.97985 52.86371,47.87263 49.02142,56.09327 C 48.66238,56.23548 15.23038,56.22933 14.89117,56.08699 z'

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        result: List[Ply] = []

        row_diff = to_pos[0] - from_pos[0]
        col_diff = to_pos[1] - from_pos[1]

        # This if statement is intentionally redundant since I do not know what it will look like when the other
        # directions are added in.
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
            elif row_diff == -1 and abs(col_diff) == 1 and game.board.tiles[to_pos].color != self.color:
                result.append([DestroyAction(to_pos), MoveAction(from_pos, to_pos)])

        elif self.direction == Direction.SOUTH:
            if to_pos not in game.board.tiles:
                # Check for single or double advance.
                if col_diff == 0 and (row_diff == 1 or (self.moves == 0 and row_diff == 2)):
                    result.append([MoveAction(from_pos, to_pos)])

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = to_pos[0] - 1, to_pos[1]
                    if (
                        captured_pawn_pos in game.board.tiles and
                        isinstance(game.board.tiles[captured_pawn_pos], Pawn) and
                        game.board.tiles[captured_pawn_pos].color != self.color
                    ):
                        event = game.n_event_by_color(game.board.tiles[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            event.ply == [MoveAction((to_pos[0] + 1, to_pos[1]), captured_pawn_pos)]
                        ):
                            result.append([DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)])

            # Check for diagonal capture.
            elif row_diff == 1 and abs(col_diff) == 1 and game.board.tiles[to_pos].color != self.color:
                result.append([DestroyAction(to_pos), MoveAction(from_pos, to_pos)])

        return result


class TestPawn(unittest.TestCase):
    # TODO: Test directions other than North and South.

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


class Rook(Piece):
    image = 'M 165,70 L 110,70 110,141 157,181 157,330 110,378 110,417 86,417 86,456 417,456 417,417 393,417 393,378 346,330 346,181 393,141 393,70 338,70 338,102 291,102 291,70 212,70 212,102 165,102 165,70 z'
    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []


class Knight(Piece):
    image = 'M 165,70 L 110,70 110,141 157,181 157,330 110,378 110,417 86,417 86,456 417,456 417,417 393,417 393,378 346,330 346,181 393,141 393,70 338,70 338,102 291,102 291,70 212,70 212,102 165,102 165,70 z'

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []


class Bishop(Piece):
    image = 'M 165,70 L 110,70 110,141 157,181 157,330 110,378 110,417 86,417 86,456 417,456 417,417 393,417 393,378 346,330 346,181 393,141 393,70 338,70 338,102 291,102 291,70 212,70 212,102 165,102 165,70 z'

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []


class Queen(Piece):
    image = 'M 165,70 L 110,70 110,141 157,181 157,330 110,378 110,417 86,417 86,456 417,456 417,417 393,417 393,378 346,330 346,181 393,141 393,70 338,70 338,102 291,102 291,70 212,70 212,102 165,102 165,70 z'

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []


class King(Piece):
    image = 'M 165,70 L 110,70 110,141 157,181 157,330 110,378 110,417 86,417 86,456 417,456 417,417 393,417 393,378 346,330 346,181 393,141 393,70 338,70 338,102 291,102 291,70 212,70 212,102 165,102 165,70 z'

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []


# Boards


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
