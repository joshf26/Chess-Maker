from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Dict, Any, Iterable
    from game import Game
    from piece import Piece
    from ply import Ply
    from color import Color
    from options import Option

from abc import ABC

from .vector2 import Vector2


class Controller(ABC):
    name = ''
    board_size = Vector2(0, 0)
    colors: List[Color] = []
    options: Dict[str, Option] = {}

    def __init__(self, game: Game, options: Dict[str, Any]):
        self.game = game

        for option, value in options.items():
            self.options[option].set_value(value)

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        pass

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Iterable[Ply]:
        return self.game.board[from_pos].get_plies(from_pos, to_pos, self.game.game_data)

    # noinspection PyMethodMayBeStatic
    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Iterable[Ply]:
        return []

    def after_ply(self) -> None:
        pass
