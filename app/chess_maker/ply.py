import json
from dataclasses import dataclass
from typing import List, Tuple, Union


@dataclass
class MoveAction:
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]


@dataclass
class DestroyAction:
    pos: Tuple[int, int]


Action = Union[MoveAction, DestroyAction]
Ply = List[Action]


def ply_to_json(ply: Ply) -> str:
    return json.dumps([{
        'type': 'move',
        'from_row': action.from_pos[0],
        'from_col': action.from_pos[1],
        'to_row': action.to_pos[0],
        'to_col': action.to_pos[1],
    } if isinstance(action, MoveAction) else {
        'type': 'destroy',
        'row': action.pos[0],
        'col': action.pos[1],
    } for action in ply])
