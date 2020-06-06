from __future__ import annotations

from typing import Dict, Generator, Iterator, Type, List, Optional, Tuple

from color import Color
from controller import Controller
from info_elements import InfoElement, InfoText
from option import BoolOption, IntOption
from packs.checkers.pieces.king import King
from packs.checkers.pieces.man import Man
from packs.standard.helpers import next_color, find_pieces, in_bounds, move_to_promotion, print_color
from piece import Piece, Direction
from ply import Ply, DestroyAction, MoveAction
from vector2 import Vector2

KING_MOVE_OFFSETS = {
    'move': [
        Vector2(1, 1),
        Vector2(1, -1),
        Vector2(-1, 1),
        Vector2(-1, -1),
    ],
    'jump': [
        Vector2(2, 2),
        Vector2(2, -2),
        Vector2(-2, 2),
        Vector2(-2, -2),
    ]
}

MOVE_OFFSETS: Dict[Type, dict] = {
    Man: {
        Direction.NORTH: {
            'move': [
                Vector2(-1, 1),
                Vector2(-1, -1),
            ],
            'jump': [
                Vector2(-2, 2),
                Vector2(-2, -2),
            ]
        },
        Direction.SOUTH: {
            'move': [
                Vector2(1, 1),
                Vector2(1, -1),
            ],
            'jump': [
                Vector2(2, 2),
                Vector2(2, -2),
            ]
        }
    },
    King: {
        Direction.NORTH: KING_MOVE_OFFSETS,
        Direction.SOUTH: KING_MOVE_OFFSETS,
    }
}


class Checkers(Controller):
    name = 'Checkers'
    board_size = Vector2(8, 8)
    colors = [
        Color.BLACK,
        Color.RED,
    ]
    options = {
        'Force Capture': BoolOption(True),
    }

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for row in [0, 1, 2, 5, 6, 7]:
            for col in range(0, 8, 2):
                if row % 2:
                    col += 1

                board[Vector2(row, col)] = Man(
                    Color.BLACK if row > 2 else Color.RED,
                    Direction.NORTH if row > 2 else Direction.SOUTH,
                )

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        piece = self.game.board[from_pos]
        plies = piece.get_plies(from_pos, to_pos, self.game.game_data)
        last_state = self.game.game_data.history[-1]

        result = []

        # Check for double jump.
        current_color, piece_that_jumped = self._current_color()
        if current_color == last_state.ply_color and self.game.board[from_pos] == piece_that_jumped:
            for ply in plies:
                if any(isinstance(action, DestroyAction) for action in ply.actions):
                    result.append(ply)
                    break

        # Check for force capture.
        elif color == piece.color and color == next_color(self.game):
            for ply in plies:
                if self._color_can_jump(color) and self.options['Force Capture']:
                    if any(isinstance(action, DestroyAction) for action in ply.actions):
                        result.append(ply)
                else:
                    result.append(ply)

        for ply in result:
            man_move_actions: Iterator[MoveAction] = filter(
                lambda action: isinstance(action, MoveAction) and isinstance(self.game.board[action.from_pos], Man),
                ply.actions
            )

            for man_move_action in man_move_actions:
                if man_move_action.to_pos.row not in [0, 7]:
                    continue

                action_piece = self.game.board[man_move_action.from_pos]
                index = ply.actions.index(man_move_action)

                ply.actions = [
                    *ply.actions[:index],
                    *move_to_promotion(man_move_action, King(action_piece.color, action_piece.direction)),
                    *ply.actions[index + 1:],
                ]

            yield ply

    def get_info(self, color: Color) -> List[InfoElement]:
        return [InfoText(f'Current turn: {print_color(self._current_color()[0])}')]

    def after_ply(self) -> None:
        for color in self.colors:
            if not self._has_legal_move(color):
                self.game.winner([Color.BLACK if color == Color.RED else Color.RED], 'No Remaining Moves')

    def _current_color(self) -> Tuple[Color, Optional[Piece]]:
        last_state = self.game.game_data.history[-1]

        if last_state.ply is not None:
            last_color_jumped = (
                isinstance(last_state.ply.actions[0], DestroyAction)
                and isinstance(last_state.ply.actions[1], MoveAction)
            )

            if last_color_jumped:
                piece_that_jumped_pos = last_state.ply.actions[1].to_pos
                piece_that_jumped = self.game.board[piece_that_jumped_pos]
                if self._piece_can_jump(piece_that_jumped_pos, piece_that_jumped):
                    return last_state.ply_color, piece_that_jumped
        else:
            return Color.BLACK, None

        return Color.BLACK if last_state.ply_color == Color.RED else Color.RED, None

    def _has_legal_move(self, color: Color):
        for pos, piece in find_pieces(self.game.board, color=color):
            piece_type_offsets = MOVE_OFFSETS[type(piece)][piece.direction]
            for offset in piece_type_offsets['move'] + piece_type_offsets['jump']:
                ply = next(piece.get_plies(pos, pos + offset, self.game.game_data), None)
                if ply is not None:
                    move_actions = filter(lambda action: isinstance(action, MoveAction), ply.actions)
                    for move_action in move_actions:
                        if in_bounds(self.board_size, move_action.to_pos):
                            return True

        return False

    def _piece_can_jump(self, pos: Vector2, piece: Piece) -> bool:
        for jump_offset in MOVE_OFFSETS[type(piece)][piece.direction]['jump']:
            for ply in piece.get_plies(pos, pos + jump_offset, self.game.game_data):
                if (
                    any(isinstance(action, MoveAction)
                    and not in_bounds(self.board_size, action.to_pos) for action in ply.actions)
                ):
                    continue

                if any(isinstance(action, DestroyAction) for action in ply.actions):
                    return True

        return False

    def _color_can_jump(self, color: Color) -> bool:
        for pos, piece in find_pieces(self.game.board, color=color):
            if self._piece_can_jump(pos, piece):
                return True

        return False


