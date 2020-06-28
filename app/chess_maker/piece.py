from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Union, Generator

from json_serializable import JsonSerializable
from pack_util import get_pack
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply
    from color import Color
    from game import GameData


class Direction(Enum):
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7


class Piece(JsonSerializable):
    name = ''
    image = ''

    def __init__(self, color: Color, direction: Direction):
        self.color = color
        self.direction = direction

        self.moves = 0

    def __repr__(self):
        return f'<{self.color} {self.__class__.__name__} facing {self.direction}>'

    def to_json(self) -> Union[dict, list]:
        return {
            'pack_id': get_pack(self),
            'piece_type_id': self.name,
            'color': self.color.value,
            'direction': self.direction.value,
        }

    def copy(self):
        return self.__class__(self.color, self.direction)

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        yield from ()
