from __future__ import annotations

from typing import Generator

from game import GameData
from piece import Piece
from pack_util import load_image
from ply import Ply, MoveAction, DestroyAction
from vector2 import Vector2


class King(Piece):
    name = 'King'
    image = load_image('checkers', 'images/king.svg')

    @staticmethod
    def move_or_capture(from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        if abs(row_diff) == abs(col_diff) == 1:
            if to_pos not in game_data.board:
                yield Ply('Move', [MoveAction(from_pos, to_pos)])

        elif abs(row_diff) == abs(col_diff) == 2:
            capture_pos = Vector2(from_pos.row + row_diff // 2, from_pos.col + col_diff // 2)
            if (
                to_pos not in game_data.board
                and capture_pos in game_data.board
                and game_data.board[capture_pos].color != game_data.board[from_pos].color
            ):
                yield Ply('Capture', [DestroyAction(capture_pos), MoveAction(from_pos, to_pos)])

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        yield from self.move_or_capture(from_pos, to_pos, game_data)
