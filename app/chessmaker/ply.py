from dataclasses import dataclass
from typing import List, Union

from .actions import Action
from .json_serializable import JsonSerializable


class NoMovesError(Exception):
    pass


@dataclass
class Ply(JsonSerializable):
    name: str
    actions: List[Action]

    def to_json(self) -> Union[dict, list]:
        return {
            'name': self.name,
            'actions': [action.to_json() for action in self.actions],
        }
