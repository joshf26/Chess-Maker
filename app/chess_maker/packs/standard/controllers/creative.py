from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Generator

from color import Color
from controller import Controller
from info_elements import InfoButton, InfoElement
from inventory_item import InventoryItem
from packs.standard.helpers import rotate_direction
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Direction
from ply import MoveAction, CreateAction, Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from piece import Piece


class Creative(Controller):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rotate_pieces_button = InfoButton('Rotate Pieces', self.rotate_pieces)

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for color in self.colors:
            with self.game.inventories[color] as inventory:
                inventory.extend([
                    InventoryItem(Pawn(color, Direction.NORTH), '∞'),
                    InventoryItem(Knight(color, Direction.NORTH), '∞'),
                    InventoryItem(Bishop(color, Direction.NORTH), '∞'),
                    InventoryItem(Rook(color, Direction.NORTH), '∞'),
                    InventoryItem(Queen(color, Direction.NORTH), '∞'),
                    InventoryItem(King(color, Direction.NORTH), '∞'),
                ])

        with self.game.public_info_elements as info:
            info.append(self.rotate_pieces_button)

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        yield Ply('Move', [MoveAction(from_pos, to_pos)])

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        yield Ply('Create', [CreateAction(piece, pos)])

    def rotate_pieces(self, color: Color) -> None:
        with self.game.inventories[color] as inventory:
            for item in inventory:
                item.piece.direction = rotate_direction(item.piece.direction)


class Creative8x8(Creative, Controller):
    name = 'Creative 8x8'
    board_size = Vector2(8, 8)


class Creative32x32(Creative, Controller):
    name = 'Creative 32x32'
    board_size = Vector2(32, 32)
