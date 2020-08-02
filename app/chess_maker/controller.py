from __future__ import annotations

from abc import ABC
from typing import List, Generator, TYPE_CHECKING, Dict

from color import Color
from vector2 import Vector2

if TYPE_CHECKING:
    from game import Game
    from piece import Piece
    from ply import Ply


class Controller(ABC):
    name = ''
    board_size = Vector2(0, 0)
    colors: List[Color] = []
    options: Dict[str, any] = {}

    def __init__(self, game: Game, options: dict):
        self.game = game
        self.options = options

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        pass

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        yield from ()

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        yield from ()

    def after_ply(self) -> None:
        pass
