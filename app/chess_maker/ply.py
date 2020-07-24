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
            'from_pos_row': self.from_pos.row,
            'from_pos_col': self.from_pos.col,
            'to_pos_row': self.to_pos.row,
            'to_pos_col': self.to_pos.col,
        }


@dataclass
class DestroyAction(JsonSerializable):
    pos: Vector2

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'destroy',
            'to_pos_row': self.pos.row,
            'to_pos_col': self.pos.col,
        }


@dataclass
class CreateAction(JsonSerializable):
    piece: Piece
    pos: Vector2

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'create',
            'to_pos_row': self.pos.row,
            'to_pos_col': self.pos.col,
            'piece': self.piece.to_json(),
        }


Action = Union[MoveAction, DestroyAction, CreateAction]


@dataclass
class Ply(JsonSerializable):
    name: str
    actions: List[Action]

    def to_json(self) -> Union[dict, list]:
        return {
            'name': self.name,
            'actions': [action.to_json() for action in self.actions],
        }
