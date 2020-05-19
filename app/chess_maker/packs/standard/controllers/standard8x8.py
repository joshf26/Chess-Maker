from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, List, Dict, Generator

from color import Color
from controller import Controller
from info_elements import InfoText, InfoElement
from packs.standard.helpers import get_color_info_texts, next_color
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Direction, Piece
from ply import DestroyAction, CreateAction
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply


class Standard8x8(Controller):
    name = 'Standard 8x8'
    size = Vector2(8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self) -> Dict[Vector2, Piece]:
        board: Dict[Vector2, Piece] = {}

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board[Vector2(row, 0)] = Rook(color, direction)
            board[Vector2(row, 1)] = Knight(color, direction)
            board[Vector2(row, 2)] = Bishop(color, direction)
            board[Vector2(row, 3)] = Queen(color, direction)
            board[Vector2(row, 4)] = King(color, direction)
            board[Vector2(row, 5)] = Bishop(color, direction)
            board[Vector2(row, 6)] = Knight(color, direction)
            board[Vector2(row, 7)] = Rook(color, direction)

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                board[Vector2(row, col)] = Pawn(color, direction)

        return board

    def get_info(self, color: Color) -> List[InfoElement]:
        next_color_name = next_color(self.game).name

        return [*get_color_info_texts(self.game, trailing_space=True), InfoText(
            f'Current Turn: <strong style="color: {next_color_name.lower()}">{next_color_name.title()}</strong>'
        )]

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        board = self.game.board
        piece = board[from_pos]

        # Make sure it is their turn.
        if piece.color != next_color(self.game):
            return

        plies = piece.get_plies(from_pos, to_pos, self.game)

        # Check for pawn promotion.
        if isinstance(piece, Pawn) and (
            (to_pos.row == 0 and piece.color == Color.WHITE)
            or (to_pos.row == 7 and piece.color == Color.BLACK)
        ):
            plies = chain(plies, [
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
            ])

        # Make sure they are not in check after each ply is complete.
        for ply in plies:
            state = self.game.next_state(color, ply)

            king_position, king = next(filter(lambda piece_data: (
                isinstance(piece_data[1], King)
                and piece_data[1].color == piece.color
            ), state.board.items()))

            threatening = False
            for position, piece in state.board.items():
                if DestroyAction(king_position) in piece.get_plies(position, king_position, self.game):
                    threatening = True
                    break

            if not threatening:
                yield ply
