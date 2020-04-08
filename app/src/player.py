from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 1


class Player:

    def __init__(self, color):
        self.color = color
