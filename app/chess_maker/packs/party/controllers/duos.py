from __future__ import annotations

from typing import Dict, List, Generator

from color import Color
from controller import Controller
from info_elements import InfoElement, InfoText
from packs.standard import Standard
from packs.standard.controllers.standard import pawn_promotions
from packs.standard.helpers import next_color, find_pieces, threatened, print_color, OFFSETS, players_without_pieces
from piece import Piece, Direction
from packs.standard.pieces.bishop import Bishop
from packs.standard.pieces.king import King
from packs.standard.pieces.knight import Knight
from packs.standard.pieces.pawn import Pawn
from packs.standard.pieces.queen import Queen
from packs.standard.pieces.rook import Rook
from ply import Ply, DestroyAction
from vector2 import Vector2


KING_COLOR = {
    Color.RED: Color.ORANGE,
    Color.BLUE: Color.PURPLE,
    Color.ORANGE: Color.ORANGE,
    Color.PURPLE: Color.PURPLE,
}

OPPONENTS = {
    Color.RED: [Color.BLUE, Color.PURPLE],
    Color.ORANGE: [Color.BLUE, Color.PURPLE],
    Color.BLUE: [Color.RED, Color.ORANGE],
    Color.PURPLE: [Color.RED, Color.ORANGE],
}


class Duos(Standard, Controller):
    name = 'Duos'
    colors = [
        Color.ORANGE,
        Color.PURPLE,
        Color.RED,
        Color.BLUE,
    ]

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for color, direction, row in zip([Color.RED, Color.BLUE], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board[Vector2(row, 0)] = Rook(color, direction)
            board[Vector2(row, 1)] = Knight(color, direction)
            board[Vector2(row, 2)] = Bishop(color, direction)
            board[Vector2(row, 3)] = Queen(color, direction)
            board[Vector2(row, 6)] = Knight(color, direction)

        for color, direction, row in zip([Color.ORANGE, Color.PURPLE], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board[Vector2(row, 4)] = King(color, direction)
            board[Vector2(row, 5)] = Bishop(color, direction)
            board[Vector2(row, 7)] = Rook(color, direction)

        for color, direction, row in zip([Color.ORANGE, Color.PURPLE], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                board[Vector2(row, col)] = Pawn(color, direction)

    def get_info(self, color: Color) -> List[InfoElement]:
        result = []

        for king_color in [Color.ORANGE, Color.PURPLE]:
            # Check if their king is in check.
            king_position, king = next(find_pieces(self.game.board, King, king_color))
            if threatened(self.game, king_position, OPPONENTS[king_color]):
                result.append(InfoText(f'{print_color(king_color)} is in check!'))

        result.append(InfoText(f'Current Turn: {print_color(next_color(self.game, list(players_without_pieces(self.game))))}'))

        return result

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        board = self.game.board
        piece = board[from_pos]

        # Make sure it is their piece and their turn.
        if color != piece.color or color != next_color(self.game, list(players_without_pieces(self.game))):
            return

        # Check for pawn promotion.
        if isinstance(piece, Pawn) and (
            (to_pos.row == 0 and piece.color in [Color.RED, Color.ORANGE])
            or (to_pos.row == 7 and piece.color in [Color.BLUE, Color.PURPLE])
        ):
            plies = pawn_promotions(piece, from_pos, to_pos)
        else:
            plies = piece.get_plies(from_pos, to_pos, self.game.game_data)

        for ply in plies:
            # Make sure they are not capturing their teammate's piece.
            captures = filter(lambda action: isinstance(action, DestroyAction), ply.actions)
            if any(board[capture.pos].color not in OPPONENTS[color] for capture in captures):
                continue

            # The owner of their team's king needs to sure they are not in check after each ply is complete.
            if color == KING_COLOR[color]:
                state = self.game.next_state(color, ply)
                king_position, king = next(find_pieces(state.board, King, color))
                if threatened(self.game, king_position, OPPONENTS[color], state):
                    continue

            yield ply

    def after_ply(self) -> None:
        color = next_color(self.game, list(players_without_pieces(self.game)))
        if color not in [Color.ORANGE, Color.PURPLE]:
            return

        king_position, king = next(find_pieces(self.game.board, King, color))

        if not self._has_legal_move(color):
            if threatened(self.game, king_position, OPPONENTS[color]):
                self.game.winner(OPPONENTS[color], 'Checkmate')
            else:
                self.game.winner([], 'Stalemate')

    def _is_legal(self, from_pos: Vector2, to_pos: Vector2) -> bool:
        if to_pos.row >= self.board_size.row or to_pos.row < 0 or to_pos.col >= self.board_size.col or to_pos.col < 0:
            return False

        piece = self.game.board[from_pos]
        plies = piece.get_plies(from_pos, to_pos, self.game.game_data)

        for ply in plies:
            # Capturing your teammate is not legal.
            captures = filter(lambda action: isinstance(action, DestroyAction), ply.actions)  # TODO: Extract function.
            if any(self.game.board[capture.pos].color not in OPPONENTS[piece.color] for capture in captures):
                continue

            state = self.game.next_state(piece.color, ply)

            king_position, king = next(find_pieces(state.board, King, piece.color))

            if not threatened(self.game, king_position, OPPONENTS[piece.color], state):
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
