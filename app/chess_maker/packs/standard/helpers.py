from __future__ import annotations

from enum import Enum
from typing import List, TYPE_CHECKING, Tuple

from board import InfoText, Board
from piece import Direction

if TYPE_CHECKING:
    from board import InfoElement
    from game import Game


def bidirectional_exclusive_range(start: int, end: int, step: int = 1) -> range:
    assert step > 0, 'step must be a positive integer'

    if start < end:
        return range(start + 1, end, step)

    return range(start - 1, end, -step)


def get_color_info_texts(game: Game, trailing_space=False) -> List[InfoElement]:
    return [InfoText(
        f'<strong style="color: {color.name.lower()}">{color.name.title()}</strong>: '
        f'{connection.nickname if (connection := game.players.get_connection(color)) is not None else "<em>Waiting...</em>"}'
    ) for color in game.board.colors] + ([InfoText('<br>')] if trailing_space else [])


def rotate_direction(direction: Direction):
    return Direction((direction.value + 1) % 8)


class Axis(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    TOP_LEFT_BOTTOM_RIGHT = 2
    BOTTOM_LEFT_TOP_RIGHT = 3


def empty_along_axis(board: Board, start: Tuple[int, int], end: Tuple[int, int]):
    row_dist = abs(end[0] - start[0])
    col_dist = abs(end[1] - start[1])

    if col_dist and not row_dist:
        axis = Axis.HORIZONTAL
    elif row_dist and not col_dist:
        axis = Axis.VERTICAL
    elif col_dist == row_dist:
        if end[0] > start[0]:
            if end[1] > start[1]:
                axis = Axis.TOP_LEFT_BOTTOM_RIGHT
            else:
                axis = Axis.BOTTOM_LEFT_TOP_RIGHT
        else:
            if end[1] > start[1]:
                axis = Axis.BOTTOM_LEFT_TOP_RIGHT
            else:
                axis = Axis.TOP_LEFT_BOTTOM_RIGHT
    else:
        raise ValueError('Start and end positions are not aligned.')

    if axis == Axis.HORIZONTAL:
        for i in bidirectional_exclusive_range(start[1], end[1]):
            if (start[0], i) in board.tiles:
                return False
    else:
        for i in bidirectional_exclusive_range(start[0], end[0]):
            if (i, start[1] + i) in board.tiles:
                return False

    return True
