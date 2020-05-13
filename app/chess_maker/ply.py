from dataclasses import dataclass
from typing import List, Union
from piece import Piece
from board import Vector2


@dataclass
class MoveAction:
    from_pos: Vector2
    to_pos: Vector2

    def to_dict(self) -> dict:
        return {
            'type': 'move',
            'from_pos': list(self.from_pos),
            'to_pos': list(self.to_pos),
        }


@dataclass
class DestroyAction:
    pos: Vector2

    def to_dict(self) -> dict:
        return {
            'type': 'destroy',
            'pos': list(self.pos),
        }


@dataclass
class CreateAction:
    piece: Piece
    pos: Vector2

    def to_dict(self) -> dict:
        return {
            'type': 'create',
            'piece': self.piece.to_dict(),
            'pos': list(self.pos),
        }


Action = Union[MoveAction, DestroyAction, CreateAction]
Ply = List[Action]


def ply_to_dicts(ply: Ply) -> List[dict]:
    return [action.to_dict() for action in ply]
