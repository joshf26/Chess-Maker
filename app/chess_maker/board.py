from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Tuple, List, Callable, Awaitable, Union
from uuid import uuid4

from color import Color
from piece import Piece

if TYPE_CHECKING:
    from ply import Ply
    from game import Game


@dataclass
class Vector2:
    row: int
    col: int

    def __add__(self, other: Vector2):
        return Vector2(self.row + other.row, self.col + other.col)

    def __sub__(self, other: Vector2):
        return Vector2(self.row - other.row, self.col - other.col)

    def __iter__(self):
        yield self.row
        yield self.col

    def __hash__(self):
        return hash(self.row) + hash(self.col)

    def copy(self):
        return Vector2(self.row, self.col)


Tiles = Dict[Vector2, Piece]


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

    def __init__(self, text: str, callback: Callable[[Color], Awaitable[None]]):
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
    size = Vector2(0, 0)
    colors = []

    def __init__(self, game: Game):
        self.game = game

        self.tiles: Tiles = {}
        self.init_board()

    def __repr__(self) -> str:
        grid = [['  '] * self.size.row for _ in range(self.size.row)]

        for position, piece in self.tiles.items():
            grid[position.row][position.col] = str(piece.color)[6] + str(piece.name)[0]

        return (
            '   ' + ''.join([f'{label:<2}' for label in range(self.size.col)]) + '\n' +
            '\n'.join([f'{index:>2} {"".join(row)}' for index, row in enumerate(grid)])
        )

    def __getitem__(self, position: Union[Vector2, Tuple[int, int]]) -> Piece:
        if isinstance(position, tuple):
            return self.tiles[Vector2(position[0], position[1])]

        return self.tiles[position]

    def __setitem__(self, position: Union[Vector2, Tuple[int, int]], piece: Piece):
        if isinstance(position, tuple):
            self.tiles[Vector2(position[0], position[1])] = piece
        else:
            self.tiles[position] = piece

    def __contains__(self, position: Union[Vector2, Tuple[int, int]]) -> bool:
        if isinstance(position, tuple):
            return Vector2(position[0], position[1]) in self.tiles

        return position in self.tiles

    def init_board(self):
        pass

    def get_info(self, color: Color) -> List[InfoElement]:
        return []

    def get_inventory(self, color: Color) -> List[Tuple[Piece, int]]:
        return []

    def process_plies(self, plies: List[Tuple[str, Ply]], from_pos: Vector2, to_pos: Vector2) -> List[Tuple[str, Ply]]:
        return plies

    def inventory_plies(self, piece: Piece, pos: Vector2) -> List[Tuple[str, Ply]]:
        return []
