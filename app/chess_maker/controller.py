from __future__ import annotations

from abc import ABC
from typing import List, Dict, Generator, TYPE_CHECKING

from color import Color
from info_elements import InfoElement
from inventory_item import InventoryItem
from piece import Piece
from ply import Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from game import Game


class Controller(ABC):
    name = ''
    board_size = Vector2(0, 0)
    colors = []

    def __init__(self, game: Game):
        self.game = game

    def init_board(self) -> Dict[Vector2, Piece]:
        pass

    def get_info(self, color: Color) -> List[InfoElement]:
        return []

    def get_inventory(self, color: Color) -> List[InventoryItem]:
        return []

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        raise StopIteration

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        raise StopIteration