from dataclasses import dataclass
from typing import List


class Action:
    pass


@dataclass
class MoveAction(Action):
    from_x: int
    from_y: int
    to_x: int
    to_y: int


@dataclass
class DestroyAction(Action):
    x: int
    y: int


Ply = List[Action]
