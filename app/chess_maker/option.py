from abc import ABC
from dataclasses import dataclass
from typing import Union, List

from json_serializable import JsonSerializable


class Option(JsonSerializable, ABC):

    def __init__(self):
        self.value = None


@dataclass
class IntOption(Option):
    default: int
    min_value: int = None
    max_value: int = None

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'int',
            'default': self.default,
            'min': self.min_value,
            'max': self.max_value,
        }


@dataclass
class BoolOption(Option):
    default: bool

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'bool',
            'default': self.default,
        }


@dataclass
class SelectOption(Option):
    default: str
    choices: List[str]

    def to_json(self) -> Union[dict, list]:
        return {
            'type': 'select',
            'default': self.default,
            'choices': self.choices,
        }
