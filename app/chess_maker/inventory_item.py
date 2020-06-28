from typing import Union
from uuid import uuid4

from json_serializable import JsonSerializable
from piece import Piece


class InventoryItem(JsonSerializable):

    def __init__(self, piece: Piece, label: str):
        self.piece = piece
        self.label = label

        self.id = str(uuid4())

    def to_json(self) -> Union[dict, list]:
        return {
            'id': self.id,
            'label': self.label,
            **self.piece.to_json(),
        }
