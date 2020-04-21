from dataclasses import dataclass
from typing import List, Tuple


class Action:
    pass


@dataclass
class MoveAction(Action):
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]


@dataclass
class DestroyAction(Action):
    pos: Tuple[int, int]


Ply = List[Action]
