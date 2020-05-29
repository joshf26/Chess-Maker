from __future__ import annotations

from typing import Dict, Generator

from color import Color
from controller import Controller
from packs.checkers.pieces.man import Man
from piece import Piece, Direction
from ply import Ply
from vector2 import Vector2


class Checkers(Controller):
    name = 'Checkers'
    board_size = Vector2(8, 8)
    colors = [
        Color.BLACK,
        Color.WHITE,
    ]

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for row in [0, 1, 2, 5, 6, 7]:
            for col in range(0, 8, 2):
                if row % 2:
                    col += 1

                board[Vector2(row, col)] = Man(
                    Color.BLACK if row > 2 else Color.WHITE,
                    Direction.NORTH if row > 2 else Direction.SOUTH,
                )

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        return self.game.board[from_pos].get_plies(from_pos, to_pos, self.game.game_data)
