from __future__ import annotations

from typing import List, Dict, Generator, TYPE_CHECKING

from color import Color
from controller import Controller
from info_elements import InfoText
from packs.standard.helpers import next_color, threatened, find_pieces, print_color, OFFSETS, opposite
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from piece import Direction
from ply import DestroyAction, CreateAction, Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from piece import Piece
    from info_elements import InfoElement


# TODO: Make this a static method of Standard.
def pawn_promotions(piece: Piece, from_pos: Vector2, to_pos: Vector2) -> List[Ply]:
    return [
        Ply('Promote to Queen', [
            DestroyAction(from_pos),
            CreateAction(Queen(piece.color, piece.direction), to_pos)
        ]),
        Ply('Promote to Knight', [
            DestroyAction(from_pos),
            CreateAction(Knight(piece.color, piece.direction), to_pos)
        ]),
        Ply('Promote to Rook', [
            DestroyAction(from_pos),
            CreateAction(Rook(piece.color, piece.direction), to_pos)
        ]),
        Ply('Promote to Bishop', [
            DestroyAction(from_pos),
            CreateAction(Bishop(piece.color, piece.direction), to_pos)
        ]),
    ]


class Chess(Controller):
    name = 'Chess'
    board_size = Vector2(8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
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

    def get_info(self, color: Color) -> List[InfoElement]:
        result = []
        ply_color = next_color(self.game)

        # Check if their king is in check.
        king_position, king = next(find_pieces(self.game.board, King, ply_color))
        if threatened(self.game, king_position, [opposite(ply_color)]):
            result.append(InfoText(f'{print_color(ply_color)} is in check!'))

        result.append(InfoText(f'Current Turn: {print_color(ply_color)}'))

        return result

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        board = self.game.board
        piece = board[from_pos]

        # Make sure they are moving their own piece.
        if color != piece.color:
            self.game.send_error(color, 'That is not your piece.')
            return

        # Make sure it is their turn.
        if color != next_color(self.game):
            self.game.send_error(color, 'It is not your turn.')
            return

        # Check for pawn promotion.
        if isinstance(piece, Pawn) and (
            (to_pos.row == 0 and piece.color == Color.WHITE)
            or (to_pos.row == 7 and piece.color == Color.BLACK)
        ):
            plies = pawn_promotions(piece, from_pos, to_pos)
        else:
            plies = list(piece.get_plies(from_pos, to_pos, self.game.game_data))
            if not plies:
                self.game.send_error(color, 'That piece cannot move like that.')
                return

        # Make sure they are not in check after each ply is complete.
        in_check = True
        for ply in plies:
            state = self.game.next_state(color, ply)

            king_position, king = next(find_pieces(state.board, King, color))

            if not threatened(self.game, king_position, [opposite(color)], state):
                yield ply
                in_check = False

        if in_check:
            self.game.send_error(color, 'That move leaves you in check.')

    def after_ply(self) -> None:
        # You cannot put yourself in checkmate, so we only need to check for the opposite color.
        color = next_color(self.game)
        king_position, king = next(find_pieces(self.game.board, King, color))

        if not self._has_legal_move(color):
            opposite_color = [opposite(color)]
            if threatened(self.game, king_position, opposite_color):
                self.game.winner(opposite_color, 'Checkmate')
            else:
                self.game.winner([], 'Stalemate')

    def _is_legal(self, from_pos: Vector2, to_pos: Vector2) -> bool:
        if to_pos.row >= self.board_size.row or to_pos.row < 0 or to_pos.col >= self.board_size.col or to_pos.col < 0:
            return False

        piece = self.game.board[from_pos]
        plies = piece.get_plies(from_pos, to_pos, self.game.game_data)

        for ply in plies:
            state = self.game.next_state(piece.color, ply)

            king_position, king = next(find_pieces(state.board, King, piece.color))

            if not threatened(self.game, king_position, [opposite(piece.color)], state):
                return True

        return False

    def _has_legal_move(self, color: Color) -> bool:
        for pos, piece in find_pieces(self.game.board, color=color):
            if isinstance(piece, Pawn):
                if piece.direction == Direction.NORTH and (
                    self._is_legal(pos, pos + Vector2(0, -1))
                    or self._is_legal(pos, pos + Vector2(0, -2))
                    or self._is_legal(pos, pos + Vector2(1, -1))
                    or self._is_legal(pos, pos + Vector2(-1, -1))
                ):
                    return True

                if piece.direction == Direction.SOUTH and (
                    self._is_legal(pos, pos + Vector2(0, 1))
                    or self._is_legal(pos, pos + Vector2(0, 2))
                    or self._is_legal(pos, pos + Vector2(1, 1))
                    or self._is_legal(pos, pos + Vector2(-1, 1))
                ):
                    return True

            if isinstance(piece, Rook) or isinstance(piece, Queen):
                for i in range(8):
                    if self._is_legal(pos, Vector2(pos.row, i)) or self._is_legal(pos, Vector2(i, pos.col)):
                        return True

            if isinstance(piece, Knight):
                if (
                    self._is_legal(pos, pos + Vector2(1, 2))
                    or self._is_legal(pos, pos + Vector2(2, 1))
                    or self._is_legal(pos, pos + Vector2(1, -2))
                    or self._is_legal(pos, pos + Vector2(2, -1))
                    or self._is_legal(pos, pos + Vector2(-1, 2))
                    or self._is_legal(pos, pos + Vector2(-2, 1))
                    or self._is_legal(pos, pos + Vector2(-1, -2))
                    or self._is_legal(pos, pos + Vector2(-2, -1))
                ):
                    return True

            if isinstance(piece, Bishop) or isinstance(piece, Queen):
                for i in range(-7, 8):
                    if self._is_legal(pos, pos + Vector2(i, i)) or self._is_legal(pos, pos + Vector2(i, i)):
                        return True

            if isinstance(piece, King):
                for offset in OFFSETS.values():
                    if self._is_legal(pos, pos + offset):
                        return True

        return False
