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
from packs.standard.pieces.wall import Wall
from piece import Direction
from ply import MoveAction, CreateAction, Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from piece import Piece
    from game import Game


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

    def __init__(self, game: Game):
        super().__init__(game)

        self.directions: Dict[Color, Direction] = {color: Direction.NORTH for color in self.colors}
        self.rotate_pieces_button = InfoButton('Rotate Pieces', self.rotate_pieces)

    def get_info(self, color: Color) -> List[InfoElement]:
        return [self.rotate_pieces_button]

    def get_inventory(self, color: Color) -> List[InventoryItem]:
        return [
            InventoryItem(Pawn(color, self.directions[color]), -1),
            InventoryItem(Knight(color, self.directions[color]), -1),
            InventoryItem(Bishop(color, self.directions[color]), -1),
            InventoryItem(Rook(color, self.directions[color]), -1),
            InventoryItem(Queen(color, self.directions[color]), -1),
            InventoryItem(King(color, self.directions[color]), -1),
            InventoryItem(Wall(color, self.directions[color]), -1),
        ]

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        yield Ply('Move', [MoveAction(from_pos, to_pos)])

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        yield Ply('Create', [CreateAction(piece, pos)])

    def rotate_pieces(self, color: Color) -> None:
        self.directions[color] = rotate_direction(self.directions[color])

        self.game.send_update_to_subscribers()


class Creative8x8(Creative, Controller):
    name = 'Creative 8x8'
    board_size = Vector2(8, 8)


class Creative32x32(Creative, Controller):
    name = 'Creative 32x32'
    board_size = Vector2(32, 32)
