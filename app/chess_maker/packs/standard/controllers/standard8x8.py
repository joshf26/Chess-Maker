from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from board import Board, InfoText, Vector2
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
    from board import InfoElement
    from game import Game


class Standard8x8(Board):
    name = 'Standard 8x8'
    size = (8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self):
        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            self[row, 0] = Rook(color, direction)
            self[row, 1] = Knight(color, direction)
            self[row, 2] = Bishop(color, direction)
            self[row, 3] = Queen(color, direction)
            self[row, 4] = King(color, direction)
            self[row, 5] = Bishop(color, direction)
            self[row, 6] = Knight(color, direction)
            self[row, 7] = Rook(color, direction)

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                self[row, col] = Pawn(color, direction)

    def get_info(self, color: Color) -> List[InfoElement]:
        result = get_color_info_texts(self.game, trailing_space=True)

        result.append(InfoText(
            f'Current Turn: <strong style="color: {self.game.current_color().name.lower()}">'
            f'{self.game.current_color().name.title()}</strong>'
        ))

        return result

    def process_plies(self, plies: List[Tuple[str, Ply]], from_pos: Vector2, to_pos: Vector2) -> List[Tuple[str, Ply]]:
        piece = self[from_pos]

        # Make sure it is their turn.
        if piece.color != self.game.current_color():
            return []

        # Make sure they are not in check after the ply is completed.
        for ply in plies:
            tiles = self.game.simulate_ply(ply[1])

            king_position, king = next(filter(lambda piece_data: (
                isinstance(piece_data[1], King)
                and piece_data[1].color == piece.color
            ), tiles.items()), None)

            for position, piece in tiles.items():
                if DestroyAction(king_position) in piece.ply_types(position, king_position, self.game):
                    # King is still in check after ply.
                    return []

        # Check for pawn promotion.
        if isinstance(piece, Pawn) and (
            (to_pos.row == 0 and piece.color == Color.WHITE)
            or (to_pos.row == 7 and piece.color == Color.BLACK)
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
