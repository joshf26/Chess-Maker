from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional, Tuple, Dict, Generator, Type

from color import Color
from info_elements import InfoText, InfoElement
from piece import Direction, Piece
from ply import Ply, DestroyAction, MoveAction
from vector2 import Vector2
from game import GameData

if TYPE_CHECKING:
    from game import Game, GameState


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
    ) for color in game.controller.colors] + ([InfoText('<br>')] if trailing_space else [])


def rotate_direction(direction: Direction) -> Direction:
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


def closest_piece_along_direction(
    game_data: GameData,
    start: Vector2,
    direction: Direction
) -> Optional[Tuple[Piece, Vector2]]:
    position = start.copy()

    while 0 <= position.row < game_data.board_size.row and 0 <= position.col < game_data.board_size.col:
        position += OFFSETS[direction]

        if position in game_data.board:
            return game_data.board[position], position

    return None


def empty_along_axis(board: Dict[Vector2, Piece], start: Vector2, end: Vector2) -> bool:
    direction = axis_direction(start, end)

    if direction is None:
        raise ValueError('Start and end positions are not aligned.')

    current_position = start.copy()
    while current_position + OFFSETS[direction] != end:
        current_position += OFFSETS[direction]
        if current_position in board:
            return False

    return True


def next_color(game: Game) -> Color:
    last_state = game.game_data.history[-1]

    if last_state.ply_color is None:
        # No turns were made yet.
        return game.controller.colors[0]

    return game.controller.colors[(game.controller.colors.index(last_state.ply_color) + 1) % len(game.controller.colors)]


def n_state_by_color(game_data: GameData, color: Color, n: int, reverse: bool = False) -> Optional[GameState]:
    current = 0
    for state in reversed(game_data.history) if reverse else game_data.history:
        if state.ply_color == color:
            current += 1

            if current == n:
                return state

    return None


def capture_or_move(
    board: Dict[Vector2, Piece],
    color: Color,
    from_pos: Vector2,
    to_pos: Vector2,
) -> Generator[Ply]:
    if to_pos in board:
        if board[to_pos].color != color:
            yield Ply('Capture', [DestroyAction(to_pos), MoveAction(from_pos, to_pos)])
    else:
        yield Ply('Move', [MoveAction(from_pos, to_pos)])


def capture_or_move_if_empty(
    board: Dict[Vector2, Piece],
    color: Color,
    from_pos: Vector2,
    to_pos: Vector2,
) -> Generator[Ply]:
    if not empty_along_axis(board, from_pos, to_pos):
        return

    yield from capture_or_move(board, color, from_pos, to_pos)


def find_pieces(
    board: Dict[Vector2, Piece],
    piece_type: Type[Piece] = None,
    color: Color = None
) -> Generator[Tuple[Vector2, Piece]]:
    yield from filter(lambda piece_data: (
        (True if piece_type is None else isinstance(piece_data[1], piece_type))
        and (True if color is None else piece_data[1].color == color)
    ), board.items())


def threatened(game: Game, pos: Vector2, by: List[Color], state: GameState = None) -> bool:
    board = game.board if state is None else state.board
    for current_pos, piece in board.items():
        if piece.color not in by:
            continue

        if any(DestroyAction(pos) in ply.actions for ply in piece.get_plies(
            current_pos,
            pos,
            GameData(
                [*game.game_data.history, state],
                game.game_data.board_size,
                game.game_data.colors,
            ) if state is not None else game.game_data,
        )):
            return True

    return False


def print_color(color: Color) -> str:
    return f'<strong style="color: {color.name.lower()}">{color.name.title()}</strong>'


def opposite(color: Color) -> Color:
    """ Returns Color.BLACK if passed Color.WHITE and returns Color.WHITE if passed COLOR.BLACK.

    Useful since many games a played by white vs black.
    """

    return Color.BLACK if color == Color.WHITE else Color.BLACK
