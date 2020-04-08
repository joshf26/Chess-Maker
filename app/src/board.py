from typing import Dict, Tuple, List

from piece import Piece
from player import Player, Color


class Board:

    def __init__(self):
        self.players = self.init_players()
        self.tiles = self.init_board()

    def init_players(self) -> List[Player]:
        raise NotImplementedError

    def init_board(self) -> Dict[Tuple[int, int], Piece]:
        raise NotImplementedError

    def get_player(self, color: Color):
        for player in self.players:
            if player.color == color:
                return player

        return None

    @property
    def ascii(self) -> str:
        size_x = max(self.tiles, key=lambda tile: tile[0])[0] + 1
        size_y = max(self.tiles, key=lambda tile: tile[1])[1] + 1

        grid = [['  '] * size_x for _ in range(size_y)]

        for position, piece in self.tiles.items():
            grid[position[1]][position[0]] = str(piece.owner.color)[6] + str(piece.__class__.__name__)[0]

        return '\n'.join([''.join(row) for row in grid])
