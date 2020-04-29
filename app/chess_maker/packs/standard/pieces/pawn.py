from __future__ import annotations
from typing import Tuple, List

from game import Game
from piece import Piece, Direction, load_image
from ply import Ply, MoveAction, DestroyAction


class Pawn(Piece):
    name = 'Pawn'
    image = load_image('standard', 'images/pawn.svg')

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
