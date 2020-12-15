from __future__ import annotations

from typing import TYPE_CHECKING, Union, Iterable

from .json_serializable import JsonSerializable
from .pack_util import get_pack
from .vector2 import Vector2
from .direction import Direction

if TYPE_CHECKING:
    from .ply import Ply
    from .color import Color
    from .game import GameData


class Piece(JsonSerializable):
    name = ''
    image = ''

    def __init__(self, color: Color, direction: Direction):
        self.color = color
        self.direction = direction

        # TODO: This is redundant since this can be implied from move history.
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

    # noinspection PyMethodMayBeStatic
    def get_plies(self, from_pos: Vector2, to_pos: Vector2, game_data: GameData) -> Iterable[Ply]:
        return ()
