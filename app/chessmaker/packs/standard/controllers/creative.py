from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chessmaker.typings import Piece
    from typing import Dict, Iterable, List

from chessmaker import Color, Controller, Direction, InventoryItem, Ply, Vector2
from chessmaker.info_elements import InfoButton
from chessmaker.actions import MoveAction, CreateAction
from ....packs.standard.pieces import Bishop, King, Knight, Pawn, Queen, Rook
from ....packs.standard.helpers import rotate_direction


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

        self.inventories: Dict[Color, List[InventoryItem]] = {color: [
            InventoryItem(Pawn(color, Direction.NORTH), '∞'),
            InventoryItem(Knight(color, Direction.NORTH), '∞'),
            InventoryItem(Bishop(color, Direction.NORTH), '∞'),
            InventoryItem(Rook(color, Direction.NORTH), '∞'),
            InventoryItem(Queen(color, Direction.NORTH), '∞'),
            InventoryItem(King(color, Direction.NORTH), '∞'),
        ] for color in self.colors}

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for color in self.colors:
            self.game.update_inventory(color, self.inventories[color])

        self.game.update_public_info([InfoButton('Rotate Pieces', self._rotate_pieces)])

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Iterable[Ply]:
        return Ply('Move', [MoveAction(from_pos, to_pos)]),

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Iterable[Ply]:
        return Ply('Create', [CreateAction(piece, pos)]),

    def _rotate_pieces(self, color: Color) -> None:
        for item in self.inventories[color]:
            item.piece.direction = rotate_direction(item.piece.direction)

        self.game.update_inventory(color, self.inventories[color])


class Creative8x8(Creative, Controller):
    name = 'Creative 8x8'
    board_size = Vector2(8, 8)


class Creative32x32(Creative, Controller):
    name = 'Creative 32x32'
    board_size = Vector2(32, 32)
