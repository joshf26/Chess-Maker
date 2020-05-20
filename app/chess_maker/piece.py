from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Union, Generator

from json_serializable import JsonSerializable
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply
    from color import Color
    from game import GameData
    from controller import Controller


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


def get_pack(obj: Union[Piece, Controller]) -> str:
    return obj.__module__.split('.')[1]


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
            'name': self.name,
            'color': self.color.value,
            'direction': self.direction.value,
        }

    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Generator[Ply]:
        yield from ()
