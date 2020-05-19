from dataclasses import dataclass
from typing import List, Union

from json_serializable import JsonSerializable
from piece import Piece
from vector2 import Vector2


@dataclass
class MoveAction(JsonSerializable):
    from_pos: Vector2
    to_pos: Vector2

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'move',
            'from_pos': list(self.from_pos),
            'to_pos': list(self.to_pos),
        }


@dataclass
class DestroyAction(JsonSerializable):
    pos: Vector2

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'destroy',
            'pos': list(self.pos),
        }


@dataclass
class CreateAction(JsonSerializable):
    piece: Piece
    pos: Vector2

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'create',
            'piece': self.piece.to_json(),
            'pos': list(self.pos),
        }


Action = Union[MoveAction, DestroyAction, CreateAction]


@dataclass
class Ply(JsonSerializable):
    name: str
    actions: List[Action]

    def to_json(self) -> Union[dict, list]:
        return [action.to_json() for action in self.actions]
