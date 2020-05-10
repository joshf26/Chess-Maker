from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from board import Board
from color import Color
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from packs.standard.pieces.wall import Wall
from ply import MoveAction, CreateAction
from piece import Direction

if TYPE_CHECKING:
    from ply import Ply
    from board import Tiles
    from piece import Piece


class Creative8x8(Board):
    name = 'Creative 8x8'
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
        return {}

    def get_inventory(self, color: Color) -> List[Tuple[Piece, int]]:
        return [
            (Pawn(color, Direction.NORTH), -1),
            (Knight(color, Direction.NORTH), -1),
            (Bishop(color, Direction.NORTH), -1),
            (Rook(color, Direction.NORTH), -1),
            (Queen(color, Direction.NORTH), -1),
            (King(color, Direction.NORTH), -1),
            (Wall(color, Direction.NORTH), -1),
        ]

    def process_plies(self, plies: List[Tuple[str, Ply]], from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> List[Tuple[str, Ply]]:
        return [('Move', [MoveAction(from_pos, to_pos)])]

    def inventory_plies(self, piece: Piece, pos: Tuple[int, int]) -> List[Tuple[str, Ply]]:
        return [('Create', [CreateAction(piece, pos)])]
