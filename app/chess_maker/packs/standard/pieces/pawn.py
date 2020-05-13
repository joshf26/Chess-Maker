from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from game import Game
from piece import Piece, Direction, load_image
from ply import Ply, MoveAction, DestroyAction

if TYPE_CHECKING:
    from board import Vector2


class Pawn(Piece):
    name = 'Pawn'
    image = load_image('standard', 'images/pawn.svg')

    def ply_types(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> List[Tuple[str, Ply]]:
        # TODO: This list is most likely redundant since pawns never have a choice.
        result: List[Tuple[str, Ply]] = []

        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # This if statement is intentionally redundant since I do not know what it will look like when the other
        # directions are added in.
        if self.direction == Direction.NORTH:
            if to_pos not in game.board.tiles:
                # Check for single or double advance.
                if col_diff == 0 and (row_diff == -1 or (
                    self.moves == 0 and row_diff == -2 and (to_pos.row + 1, to_pos.col) not in game.board.tiles
                )):
                    result.append(('Move', [MoveAction(from_pos, to_pos)]))

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = to_pos.row + 1, to_pos.col
                    if (
                        captured_pawn_pos in game.board.tiles and
                        isinstance(game.board.tiles[captured_pawn_pos], Pawn) and
                        game.board.tiles[captured_pawn_pos].color != self.color
                    ):
                        event = game.n_event_by_color(game.board.tiles[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            event.ply == [MoveAction((to_pos.row - 1, to_pos.col), captured_pawn_pos)]
                        ):
                            result.append(('En Passant', [DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)]))

            # Check for diagonal capture.
            elif row_diff == -1 and abs(col_diff) == 1 and game.board.tiles[to_pos].color != self.color:
                result.append(('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)]))

        elif self.direction == Direction.SOUTH:
            if to_pos not in game.board.tiles:
                # Check for single or double advance.
                if col_diff == 0 and (row_diff == 1 or (
                    self.moves == 0 and row_diff == 2 and (to_pos.row - 1, to_pos.col) not in game.board.tiles
                )):
                    result.append(('Move', [MoveAction(from_pos, to_pos)]))

                # Check for en passant.
                if abs(col_diff) == 1:
                    captured_pawn_pos = to_pos.row - 1, to_pos.col
                    if (
                        captured_pawn_pos in game.board.tiles and
                        isinstance(game.board.tiles[captured_pawn_pos], Pawn) and
                        game.board.tiles[captured_pawn_pos].color != self.color
                    ):
                        event = game.n_event_by_color(game.board.tiles[captured_pawn_pos].color, 1, reverse=True)
                        if (
                            event is not None and
                            event.ply == [MoveAction((to_pos.row + 1, to_pos.col), captured_pawn_pos)]
                        ):
                            result.append(('En Passant', [DestroyAction(captured_pawn_pos), MoveAction(from_pos, to_pos)]))

            # Check for diagonal capture.
            elif row_diff == 1 and abs(col_diff) == 1 and game.board.tiles[to_pos].color != self.color:
                result.append(('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)]))

        return result
