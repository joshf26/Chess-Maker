from __future__ import annotations

from dataclasses import dataclass
from typing import Generator


@dataclass
class Vector2:
    row: int
    col: int

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.row + other.row, self.col + other.col)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.row - other.row, self.col - other.col)

    def __eq__(self, other: Vector2):
        return self.row == other.row and self.col == other.col

    def __iter__(self) -> Generator[int]:
        yield self.row
        yield self.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def copy(self) -> Vector2:
        return Vector2(self.row, self.col)
