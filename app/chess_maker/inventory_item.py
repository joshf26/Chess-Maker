from dataclasses import dataclass

from piece import Piece


@dataclass
class InventoryItem:
    piece: Piece
    quantity: int
