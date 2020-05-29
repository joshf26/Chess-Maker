from __future__ import annotations

from typing import Generator

from game import GameData
from piece import Piece, load_image
from ply import Ply, MoveAction
from vector2 import Vector2


class Man(Piece):
    name = 'Man'
    image = load_image('checkers', 'images/man.svg')

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        if to_pos == from_pos or abs(row_diff) != abs(col_diff):
            return

        yield Ply('Test', [MoveAction(from_pos, to_pos)])
