from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import List, TYPE_CHECKING, Optional, Tuple, Dict, Generator, Type, Union, Hashable, Iterator, Iterable

from PIL import Image

from color import Color
from piece import Direction, Piece
from ply import Ply, DestroyAction, MoveAction, Action, CreateAction
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

CARDINALS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
ORDINALS = [Direction.NORTH_EAST, Direction.SOUTH_EAST, Direction.SOUTH_WEST, Direction.NORTH_WEST]


def axis_direction(from_pos: Vector2, to_pos: Vector2) -> Optional[Direction]:
    """ Returns a direction that points from `from_pos` to `to_pos`.

    If pieces are not aligned on an axis, this function returns None. """

    row_diff = to_pos.row - from_pos.row
    col_diff = to_pos.col - from_pos.col

    if not row_diff and not col_diff:
        return None
    elif row_diff and not col_diff:
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


def rotate_direction(direction: Direction, n=1, counter_clockwise=False) -> Direction:
    """ Rotates a direction `n` times in the specified movement direction. """

    index = direction.value - (n if counter_clockwise else -n)
    return Direction(index % 8)


def board_range(start: Vector2, end: Vector2, include_start=True, include_end=False) -> Generator[Vector2]:
    """ Similar to python's built-in `range` object, but works along a board. """

    if (direction := axis_direction(start, end)) is None:
        raise ValueError('Start and end positions are not aligned.')

    if include_start:
        yield start

    current = start.copy()
    while current + OFFSETS[direction] != end:
        current += OFFSETS[direction]
        yield current

    if include_end:
        yield end


def closest_piece_along_axis(
    game_data: GameData,
    start: Vector2,
    direction: Direction
) -> Optional[Tuple[Piece, Vector2]]:
    """ Finds the closest piece from `start` along `direction`.

    This is used to find if the nearest piece is a rook to check for castling. """

    position = start.copy()

    while 0 <= position.row < game_data.board_size.row and 0 <= position.col < game_data.board_size.col:
        position += OFFSETS[direction]

        if position in game_data.board:
            return game_data.board[position], position

    return None


def empty_along_axis(board: Dict[Vector2, Piece], start: Vector2, end: Vector2, include_end=False) -> bool:
    """ Loops through two board points aligned on an axis and returns True if there are no pieces between them. """

    if (direction := axis_direction(start, end)) is None:
        raise ValueError('Start and end positions are not aligned.')

    current_position = start.copy()
    while current_position + OFFSETS[direction] != end:
        current_position += OFFSETS[direction]
        if current_position in board:
            return False

    if include_end and current_position + OFFSETS[direction] in board:
        return False

    return True


def next_color(game: Game, skip_colors: List[Color] = None) -> Optional[Color]:
    """ Returns the color after the color of the last ply. Order is based off of the controller's `colors` list. """

    if skip_colors is None:
        skip_colors = []

    last_state = game.game_data.history[-1]
    available_colors = [color for color in game.controller.colors if color not in skip_colors]

    if last_state.ply_color is None:
        # No turns were made yet.
        return available_colors[0]

    return available_colors[(available_colors.index(last_state.ply_color) + 1) % len(available_colors)]


def players_without_pieces(game: Game) -> Iterable[Color]:
    """ Generates an iterator that iterates through all colors that do not have any pieces on the board.

    This function does not check inventories. """

    return filter(lambda color: next(find_pieces(game.board, color=color), None) is None, game.controller.colors)


def n_state_by_color(game_data: GameData, color: Color, n: int, reverse: bool = False) -> Optional[GameState]:
    """ Searches backwards or forwards through the game history and grabs the `n`th state that `color` moved in.

    Useful for looking at previous moves. For example, Pawns use this to check if en passant is available. """

    return next(islice(filter(
        lambda state: state.ply_color == color,
        reversed(game_data.history) if reverse else game_data.history,
    ), n, None), None)


def capture_or_move(board: Dict[Vector2, Piece], color: Color, from_pos: Vector2, to_pos: Vector2) -> Ply:
    """ Returns either a capture or move ply depending on whether an other-color piece exists on `to_pos`. """

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
    """ Returns call to `capture_or_move` if call to `empty_along_axis` is True.

    This is a very common pattern in creating pieces. """

    if not empty_along_axis(board, from_pos, to_pos):
        return

    yield capture_or_move(board, color, from_pos, to_pos)


def find_pieces(
    board: Dict[Vector2, Piece],
    piece_type: Type[Piece] = None,
    color: Color = None,
) -> Iterator[Tuple[Vector2, Piece]]:
    """ Generates an iterator that iterates through all pieces on the board that match the given piece type and
    color."""

    return filter(lambda piece_data: (
        (True if piece_type is None else isinstance(piece_data[1], piece_type))
        and (True if color is None else piece_data[1].color == color)
    ), board.items())


def threatened(game: Game, pos: Vector2, by: List[Color], state: GameState = None) -> bool:
    """ Check if a piece is threatened by a color.

    This simply loops through all pieces belonging to the `by` colors and checks if any plies from their position to
    `pos` contain a DestroyAction.

    Warning: this function only checks piece plies. If a controller inserts a DestroyAction, this function will not
    check for it. """

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
    """ Generates HTML for displaying a color in the info panel.

    The text is made bold and is colored to match the color given. """

    return f'<strong style="color: {color.name.lower()}">{color.name.title()}</strong>'


def opposite(color: Color) -> Color:
    """ Returns Color.BLACK if passed Color.WHITE and returns Color.WHITE if passed COLOR.BLACK.

    Useful since many games a played by white vs black.
    """

    return Color.WHITE if color == Color.BLACK else Color.BLACK


def in_bounds(board_size: Vector2, pos: Vector2) -> bool:
    """ Returns True if pos is within bounds of a board with size board_size. """

    return 0 <= pos.row < board_size.row and 0 <= pos.col < board_size.col


def move_to_promotion(action: MoveAction, piece: Piece) -> List[Action]:
    """ Transforms a MoveAction into a promotion action (destroy original piece and create new piece).

    Useful if a piece generates a move action but the controller wants to turn it into a promotion. Like a pawn
    making it to the other side of the board."""

    return [DestroyAction(action.from_pos), CreateAction(piece, action.to_pos)]


@dataclass
class ImageMapData:
    size: Vector2
    data: Dict[Hashable, List[Vector2]]


def image_to_map(
    pack_path: str,
    image_path: str,
    color_mapping: Union[Dict[int, Hashable], Dict[tuple, Hashable]],
) -> ImageMapData:
    image = Image.open(f'chess_maker/packs/{pack_path}/{image_path}')
    data = image.getdata()
    result: Dict[Hashable, List[Vector2]] = {}

    for row in range(image.height):
        for col in range(image.width):
            pixel = data[row * image.width + col]
            if pixel in color_mapping:
                mapping = color_mapping[pixel]
                if mapping not in result:
                    result[mapping] = []

                result[mapping].append(Vector2(row, col))
            else:
                print(f'WARNING: No mapping for color {pixel} found. Ignoring pixel at row {row}, col {col} with color.')

    return ImageMapData(
        Vector2(image.height, image.width),
        result,
    )
