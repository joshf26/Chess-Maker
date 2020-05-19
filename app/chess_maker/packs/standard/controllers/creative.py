from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, List, Dict

from board import Board, InfoButton
from color import Color
from packs.standard.helpers import rotate_direction
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
    from game import Game
    from board import InfoElement, Vector2


class Creative(Board):
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

    def get_inventory(self, color: Color) -> List[Tuple[Piece, int]]:
        return [
            (Pawn(color, self.directions[color]), -1),
            (Knight(color, self.directions[color]), -1),
            (Bishop(color, self.directions[color]), -1),
            (Rook(color, self.directions[color]), -1),
            (Queen(color, self.directions[color]), -1),
            (King(color, self.directions[color]), -1),
            (Wall(color, self.directions[color]), -1),
        ]

    def process_plies(self, plies: List[Tuple[str, Ply]], from_pos: Vector2, to_pos: Vector2) -> List[Tuple[str, Ply]]:
        return [('Move', [MoveAction(from_pos, to_pos)])]

    def inventory_plies(self, piece: Piece, pos: Vector2) -> List[Tuple[str, Ply]]:
        return [('Create', [CreateAction(piece, pos)])]

    async def rotate_pieces(self, color: Color):
        self.directions[color] = rotate_direction(self.directions[color])

        await self.game.send_update_to_subscribers()


class Creative8x8(Creative, Board):
    name = 'Creative 8x8'
    size = (8, 8)


class Creative32x32(Creative, Board):
    name = 'Creative 32x32'
    size = (32, 32)
