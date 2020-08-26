from abc import ABC
from dataclasses import dataclass
from typing import Union, List, Any

from json_serializable import JsonSerializable
from user_error import user_error


class Option(JsonSerializable, ABC):

    def __init__(self):
        self._value = None

    def set_value(self, value: Any) -> None:
        self._value = value

    @property
    def value(self) -> Any:
        if not hasattr(self, '_value') or self._value is None:
            user_error(
                "Option value accessed before initialization. Make sure you call super().__init__(*args, **kwargs) as "
                "the first line in your game's constructor."
            )

        return self._value


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
