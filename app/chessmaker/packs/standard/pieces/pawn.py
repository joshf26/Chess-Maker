from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Generator
    from chessmaker import GameData, Vector2

from chessmaker import Direction, Ply, Piece, Vector2
from chessmaker.actions import MoveAction, DestroyAction
from ..helpers import n_state_by_color, load_image


class Pawn(Piece):
    name = 'Pawn'
    image = load_image('standard', 'images/pawn.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # This if statement is intentionally redundant since I do not know what it will look like when the other
        # directions are added in.
        if self.direction == Direction.NORTH:
            if to_pos not in game_data.board:
                # Check for single advance.
                if col_diff == 0 and row_diff == -1:
                    yield Ply('Single Advance', [MoveAction(from_pos, to_pos)])

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = Vector2(to_pos.row + 1, to_pos.col)
                    if (
                        captured_pawn_pos in game_data.board and
                        isinstance(game_data.board[captured_pawn_pos], Pawn) and
                        game_data.board[captured_pawn_pos].color != self.color
                    ):
                        event = n_state_by_color(game_data, game_data.board[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            MoveAction(Vector2(to_pos.row - 1, to_pos.col), captured_pawn_pos) in event.ply.actions
                        ):
                            yield Ply('En Passant', [DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)])

            # Check for diagonal capture.
            elif row_diff == -1 and abs(col_diff) == 1 and game_data.board[to_pos].color != self.color:
                yield Ply('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])

        elif self.direction == Direction.SOUTH:
            if to_pos not in game_data.board:
                # Check for single advance.
                if col_diff == 0 and row_diff == 1:
                    yield Ply('Single Advance', [MoveAction(from_pos, to_pos)])

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = Vector2(to_pos.row - 1, to_pos.col)
                    if (
                        captured_pawn_pos in game_data.board and
                        isinstance(game_data.board[captured_pawn_pos], Pawn) and
                        game_data.board[captured_pawn_pos].color != self.color
                    ):
                        event = n_state_by_color(game_data, game_data.board[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            MoveAction(Vector2(to_pos.row + 1, to_pos.col), captured_pawn_pos) in event.ply.actions
                        ):
                            yield Ply('En Passant', [DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)])

            # Check for diagonal capture.
            elif row_diff == 1 and abs(col_diff) == 1 and game_data.board[to_pos].color != self.color:
                yield Ply('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])
