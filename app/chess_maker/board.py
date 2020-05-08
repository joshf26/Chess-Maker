from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple, List, Callable, Awaitable
from uuid import uuid4

from color import Color

if TYPE_CHECKING:
    from piece import Piece
    from ply import Ply
    from game import Game

    Tiles = Dict[Tuple[int, int], Piece]


class InfoElement:

    def to_dict(self) -> dict:
        raise NotImplementedError


class InfoText(InfoElement):

    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> dict:
        return {
            'type': 'text',
            'text': self.text,
        }


class InfoButton(InfoElement):

    def __init__(self, text: str, callback: Callable[[], None]):
        self.text = text
        self.callback = callback

        self.id = str(uuid4())

    def to_dict(self) -> dict:
        return {
            'type': 'button',
            'id': self.id,
            'text': self.text,
        }


class Board:
    name = 'Custom'
    size = (0, 0)
    colors = []

    def __init__(self, game: Game):
        self.game = game

        self.tiles = self.init_board()

    def __repr__(self) -> str:
        grid = [['  '] * self.size[0] for _ in range(self.size[0])]

        for position, piece in self.tiles.items():
            grid[position[0]][position[1]] = str(piece.color)[6] + str(piece.name)[0]

        return (
            '   ' + ''.join([f'{label:<2}' for label in range(self.size[1])]) + '\n' +
            '\n'.join([f'{index:>2} {"".join(row)}' for index, row in enumerate(grid)])
        )

    def init_board(self) -> Tiles:
        raise NotImplementedError

    def get_info(self, color: Color) -> List[InfoElement]:
        return []

    def get_inventory(self, color: Color) -> List[Tuple[Piece, int]]:
        return []

    def process_plies(self, plies: List[Ply], from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> List[Ply]:
        return plies

    def inventory_plies(self, piece: Piece, pos: Tuple[int, int]) -> List[Ply]:
        return []
