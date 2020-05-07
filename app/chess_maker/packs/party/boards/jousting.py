from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from board import Board
from color import Color
from packs.standard.pieces.knight import Knight
from piece import Direction

if TYPE_CHECKING:
    from ply import Ply
    from game import Game
    from board import Tiles


class Jousting(Board):
    name = 'Jousting'
    size = (8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
        Color.RED,
        Color.ORANGE,
        Color.YELLOW,
        Color.GREEN,
        Color.BLUE,
        Color.PURPLE,
    ]

    def init_board(self) -> Tiles:
        board: Tiles = {
            (0, 2): Knight(Color.WHITE, Direction.NORTH),
            (0, 5): Knight(Color.BLACK, Direction.NORTH),
            (2, 7): Knight(Color.RED, Direction.NORTH),
            (5, 7): Knight(Color.ORANGE, Direction.NORTH),
            (7, 5): Knight(Color.YELLOW, Direction.NORTH),
            (7, 2): Knight(Color.GREEN, Direction.NORTH),
            (5, 0): Knight(Color.BLUE, Direction.NORTH),
            (2, 0): Knight(Color.PURPLE, Direction.NORTH),
        }

        return board

    def process_plies(
        self,
        plies: List[Ply],
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return plies
