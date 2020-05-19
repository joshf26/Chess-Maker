from abc import ABC
from typing import Callable, Awaitable
from uuid import uuid4

from color import Color
from json_serializable import JsonSerializable


class InfoElement(JsonSerializable, ABC):
    pass


class InfoText(InfoElement):

    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> dict:
        return {
            'type': 'text',
            'text': self.text,
        }


class InfoButton(InfoElement):

    def __init__(self, text: str, callback: Callable[[Color], Awaitable[None]]):
        self.text = text
        self.callback = callback

        self.id = str(uuid4())

    def to_dict(self) -> dict:
        return {
            'type': 'button',
            'id': self.id,
            'text': self.text,
        }
