from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from piece import Piece

    Tiles = Dict[Tuple[int, int], Piece]


class Board:
    name = 'Custom'
    size = (0, 0)
    colors = []

    def __init__(self):
        self.tiles = self.init_board()

    def init_board(self) -> Tiles:
        raise NotImplementedError

    def __repr__(self) -> str:
        grid = [['  '] * self.size[0] for _ in range(self.size[0])]

        for position, piece in self.tiles.items():
            grid[position[0]][position[1]] = str(piece.color)[6] + str(piece.name)[0]

        return (
            '   ' + ''.join([f'{label:<2}' for label in range(self.size[1])]) + '\n' +
            '\n'.join([f'{index:>2} {"".join(row)}' for index, row in enumerate(grid)])
        )
