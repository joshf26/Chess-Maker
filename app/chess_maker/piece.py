from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Set, Tuple

if TYPE_CHECKING:
    from ply import Ply
    from color import Color
    from game import Game


class Direction(Enum):
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7


def load_image(pack_path: str, image_path: str) -> str:
    with open(f'chess_maker/packs/{pack_path}/{image_path}') as file:
        return file.read()


class Piece:
    name = 'Piece'
    image = ''

    def __init__(self, color: Color, direction: Direction):
        self.color = color
        self.direction = direction

        self.moves = 0

    def __repr__(self):
        return f'<{self.color} {self.__class__.__name__} facing {self.direction}>'

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'color': self.color.value,
            'direction': self.direction.value,
        }

    def ply_types(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], game: Game) -> Set[Ply]:
        raise NotImplementedError
