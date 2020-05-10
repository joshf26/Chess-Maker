import json
from dataclasses import dataclass
from typing import List, Tuple, Union
from piece import Piece


@dataclass
class MoveAction:
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]

    def to_dict(self) -> dict:
        return {
            'type': 'move',
            'from_pos': list(self.from_pos),
            'to_pos': list(self.to_pos),
        }


@dataclass
class DestroyAction:
    pos: Tuple[int, int]

    def to_dict(self) -> dict:
        return {
            'type': 'destroy',
            'pos': list(self.pos),
        }


@dataclass
class CreateAction:
    piece: Piece
    pos: Tuple[int, int]

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
