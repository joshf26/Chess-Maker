from __future__ import annotations

from enum import Enum
from typing import List, TYPE_CHECKING, Optional, Tuple

from board import InfoText, Board, Vector2
from piece import Direction, Piece

if TYPE_CHECKING:
    from board import InfoElement
    from game import Game


OFFSETS = {
    Direction.NORTH: Vector2(-1, 0),
    Direction.NORTH_EAST: Vector2(-1, 1),
    Direction.EAST: Vector2(0, 1),
    Direction.SOUTH_EAST: Vector2(1, 1),
    Direction.SOUTH: Vector2(1, 0),
    Direction.SOUTH_WEST: Vector2(1, -1),
    Direction.WEST: Vector2(0, -1),
    Direction.NORTH_WEST: Vector2(-1, -1),
}


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


def axis_direction(from_pos: Vector2, to_pos: Vector2) -> Optional[Direction]:
    row_diff = to_pos.row - from_pos.row
    col_diff = to_pos.col - from_pos.col

    if row_diff and not col_diff:
        return Direction.SOUTH if row_diff > 0 else Direction.NORTH
    elif col_diff and not row_diff:
        return Direction.EAST if col_diff > 0 else Direction.WEST
    elif abs(row_diff) == abs(col_diff):
        if row_diff > 0:
            return Direction.SOUTH_EAST if col_diff > 0 else Direction.SOUTH_WEST
        else:
            return Direction.NORTH_EAST if col_diff > 0 else Direction.NORTH_WEST
    else:
        return None


def closest_piece_along_direction(board: Board, start: Vector2, direction: Direction) -> Optional[Tuple[Piece, Vector2]]:
    position = start.copy()

    while 0 <= position.row < board.size[0] and 0 <= position.col < board.size[1]:
        position += OFFSETS[direction]

        if position in board.tiles:
            return board.tiles[position], position

    return None


class Axis(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    TOP_LEFT_BOTTOM_RIGHT = 2
    BOTTOM_LEFT_TOP_RIGHT = 3


def empty_along_axis(board: Board, start: Vector2, end: Vector2):
    row_dist = abs(end.row - start.row)
    col_dist = abs(end.col - start.col)

    if col_dist and not row_dist:
        axis = Axis.HORIZONTAL
    elif row_dist and not col_dist:
        axis = Axis.VERTICAL
    elif col_dist == row_dist:
        if end.row > start.row:
            if end.col > start.col:
                axis = Axis.TOP_LEFT_BOTTOM_RIGHT
            else:
                axis = Axis.BOTTOM_LEFT_TOP_RIGHT
        else:
            if end.col > start.col:
                axis = Axis.BOTTOM_LEFT_TOP_RIGHT
            else:
                axis = Axis.TOP_LEFT_BOTTOM_RIGHT
    else:
        raise ValueError('Start and end positions are not aligned.')

    if axis == Axis.HORIZONTAL:
        for i in bidirectional_exclusive_range(start.col, end.col):
            if (start.row, i) in board.tiles:
                return False
    else:
        for i in bidirectional_exclusive_range(start.row, end.row):
            if (i, start.col + i) in board.tiles:
                return False

    return True
