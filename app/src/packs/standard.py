from typing import Optional, Dict, Tuple, Set

from board import Board
from piece import Piece
from player import Player, Color


# Boards


class Standard8x8(Board):

    def init_players(self) -> Set[Player]:
        return {
            Player(Color.WHITE),
            Player(Color.BLACK),
        }

    def init_board(self) -> Dict[Tuple[int, int], Piece]:
        board = {}

        players = [
            self.get_player(Color.WHITE),
            self.get_player(Color.BLACK),
        ]

        for player, row in zip(players, [7, 0]):
            board[0, row] = Rook(player)
            board[7, row] = Rook(player)
            board[1, row] = Knight(player)
            board[6, row] = Knight(player)
            board[2, row] = Bishop(player)
            board[5, row] = Bishop(player)
            board[3, row] = Queen(player)
            board[4, row] = King(player)

        for col in range(8):
            for player, row in zip(players, [6, 1]):
                board[col, row] = Pawn(player)

        return board

    def space_valid(self, x: int, y: int, player: Player, piece: Piece) -> bool:
        return 0 <= x <= 8 and 0 <= y <= 8

    def upgrade(self, x: int, y: int, player: Player, piece: Piece) -> Optional[Piece]:
        if isinstance(piece, Pawn):
            return

        if player.color == Color.WHITE and y == 0:
            return Queen(player)

        if player.color == Color.BLACK and y == 8:
            return Queen(player)


# Pieces


class Pawn(Piece):
    pass


class Rook(Piece):
    pass


class Knight(Piece):
    pass


class Bishop(Piece):
    pass


class Queen(Piece):
    pass


class King(Piece):
    pass
