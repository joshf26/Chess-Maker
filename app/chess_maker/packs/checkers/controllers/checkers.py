from __future__ import annotations

from typing import Dict, Generator, Iterator, Type, List

from color import Color
from controller import Controller
from packs.checkers.pieces.king import King
from packs.checkers.pieces.man import Man
from packs.standard.helpers import next_color, find_pieces, in_bounds, move_to_promotion
from piece import Piece, Direction
from ply import Ply, DestroyAction, MoveAction
from vector2 import Vector2


MOVE_OFFSETS: Dict[Type, Dict[str, List[Vector2]]] = {
    Man: {
        'move': [
            Vector2(-1, 1),
            Vector2(-1, -1),
        ],
        'jump': [
            Vector2(-2, 2),
            Vector2(-2, -2),
        ]
    },
    King: {
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
    },
}


JUMP_OFFSETS = [
    Vector2(2, 2),
    Vector2(2, -2),
    Vector2(-2, 2),
    Vector2(-2, -2),
]


class Checkers(Controller):
    name = 'Checkers'
    board_size = Vector2(8, 8)
    colors = [
        Color.BLACK,
        Color.RED,
    ]

    def can_jump(self, color: Color) -> bool:
        for pos, piece in find_pieces(self.game.board, color=color):
            for jump_offset in JUMP_OFFSETS:
                for ply in piece.get_plies(pos, pos + jump_offset, self.game.game_data):
                    if any(isinstance(action, MoveAction) and not in_bounds(self.board_size, action.to_pos) for action in ply.actions):
                        continue

                    if any(isinstance(action, DestroyAction) for action in ply.actions):
                        return True

        return False

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
        last_color_jumped = None if last_state.ply is None else (
                any(isinstance(action, DestroyAction) for action in last_state.ply.actions)
                and any(isinstance(action, MoveAction) for action in last_state.ply.actions)
        )

        result = []

        if last_color_jumped and self.can_jump(last_state.ply_color):
            if color == last_state.ply_color:
                for ply in plies:
                    if any(isinstance(action, DestroyAction) for action in ply.actions):
                        result.append(ply)

        elif color == piece.color and color == next_color(self.game):
            for ply in plies:
                if self.can_jump(color):
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

    def after_ply(self) -> None:
        for color in self.colors:
            if not self._has_legal_move(color):
                self.game.winner([Color.BLACK if color == Color.RED else Color.RED], 'No Remaining Moves')

    def _has_legal_move(self, color: Color):
        for pos, piece in find_pieces(self.game.board, color=color):
            piece_type_offsets = MOVE_OFFSETS[type(piece)]
            for offset in piece_type_offsets['move'] + piece_type_offsets['jump']:
                ply = next(piece.get_plies(pos, pos + offset, self.game.game_data), None)
                if ply is not None:
                    move_actions = filter(lambda action: isinstance(action, MoveAction), ply.actions)
                    for move_action in move_actions:
                        if in_bounds(self.board_size, move_action.to_pos):
                            return True

        return False


