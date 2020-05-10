from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from board import Board, InfoElement, InfoText
from color import Color
from packs.standard.helpers import get_color_info_texts
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Direction
from ply import DestroyAction, CreateAction

if TYPE_CHECKING:
    from ply import Ply
    from board import Tiles


class Standard8x8(Board):
    name = 'Standard 8x8'
    size = (8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self) -> Tiles:
        board: Tiles = {}

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board[row, 0] = Rook(color, direction)
            board[row, 1] = Knight(color, direction)
            board[row, 2] = Bishop(color, direction)
            board[row, 3] = Queen(color, direction)
            board[row, 4] = King(color, direction)
            board[row, 5] = Bishop(color, direction)
            board[row, 6] = Knight(color, direction)
            board[row, 7] = Rook(color, direction)

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                board[row, col] = Pawn(color, direction)

        return board

    def get_info(self, color: Color) -> List[InfoElement]:
        result = get_color_info_texts(self.game, trailing_space=True)

        result.append(InfoText(
            f'Current Turn: <strong style="color: {self.game.current_color().name.lower()}">'
            f'{self.game.current_color().name.title()}</strong>'
        ))

        return result

    def process_plies(self, plies: List[Tuple[str, Ply]], from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> List[Tuple[str, Ply]]:
        piece = self.tiles[from_pos]

        # Make sure it is their turn.
        if piece.color != self.game.current_color():
            return []

        # Check for pawn promotion.
        if isinstance(piece, Pawn) and (
            (to_pos[0] == 0 and piece.color == Color.WHITE)
            or (to_pos[0] == 7 and piece.color == Color.BLACK)
        ):
            return [
                ('Promote to Queen', [
                    DestroyAction(from_pos),
                    CreateAction(Queen(piece.color, piece.direction), to_pos)
                ]),
                ('Promote to Knight', [
                    DestroyAction(from_pos),
                    CreateAction(Knight(piece.color, piece.direction), to_pos)
                ]),
                ('Promote to Rook', [
                    DestroyAction(from_pos),
                    CreateAction(Rook(piece.color, piece.direction), to_pos)
                ]),
                ('Promote to Bishop', [
                    DestroyAction(from_pos),
                    CreateAction(Bishop(piece.color, piece.direction), to_pos)
                ]),
            ]

        return plies
