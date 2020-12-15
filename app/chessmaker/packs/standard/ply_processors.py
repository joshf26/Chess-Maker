from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Iterable
    from chessmaker.typings import Game

from dataclasses import dataclass

from chessmaker import Color, Ply, NoMovesError, Vector2
from chessmaker.actions import DestroyAction, CreateAction, MoveAction
from .pieces import Bishop, King, Knight, Pawn, Queen, Rook
from .helpers import next_color, empty_along_axis, threatened, opposite, board_range, find_pieces


from abc import ABC, abstractmethod


class PlyProcessor(ABC):
    @abstractmethod
    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        pass


class OnlyPieceOwner(PlyProcessor):
    def __init__(self, game: Game, color: Color, from_pos: Vector2):
        self.game = game
        self.color = color
        self.from_pos = from_pos

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        if self.color != self.game.board[self.from_pos].color:
            raise NoMovesError('That is not your piece.')

        return plies


class OnlyOnOwnTurn(PlyProcessor):
    def __init__(self, game: Game, color: Color):
        self.game = game
        self.color = color

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        if self.color != next_color(self.game):
            raise NoMovesError('It is not your turn.')

        return plies


class AllowPawnPromotion(PlyProcessor):
    def __init__(self, game: Game, from_pos: Vector2, to_pos: Vector2):
        self.game = game
        self.from_pos = from_pos
        self.to_pos = to_pos

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        piece = self.game.board[self.from_pos]
        if isinstance(piece, Pawn) and self.to_pos.row in [0, 7]:
            return (
                Ply('Promote to Queen', [
                    DestroyAction(self.from_pos),
                    CreateAction(Queen(piece.color, piece.direction), self.to_pos)
                ]),
                Ply('Promote to Knight', [
                    DestroyAction(self.from_pos),
                    CreateAction(Knight(piece.color, piece.direction), self.to_pos)
                ]),
                Ply('Promote to Rook', [
                    DestroyAction(self.from_pos),
                    CreateAction(Rook(piece.color, piece.direction), self.to_pos)
                ]),
                Ply('Promote to Bishop', [
                    DestroyAction(self.from_pos),
                    CreateAction(Bishop(piece.color, piece.direction), self.to_pos)
                ]),
            )
        else:
            return plies


class AllowPawnDoubleAdvance(PlyProcessor):
    def __init__(self, game: Game, color: Color, from_pos: Vector2, to_pos: Vector2):
        self.game = game
        self.color = color
        self.from_pos = from_pos
        self.to_pos = to_pos

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        piece = self.game.board[self.from_pos]
        pos_diff = abs(self.to_pos - self.from_pos)

        if not isinstance(piece, Pawn):
            yield from plies
            return

        if (
            pos_diff.col == 0
            and empty_along_axis(self.game.board, self.from_pos, self.to_pos, include_end=True)
            and (
                (self.color == Color.WHITE and self.from_pos.row == 6 and self.to_pos.row == 4)
                or (self.color == Color.BLACK and self.from_pos.row == 1 and self.to_pos.row == 3)
            )
        ):
            yield Ply('Double Advance', [MoveAction(self.from_pos, self.to_pos)])
        elif pos_diff.row == 2:  # TODO: This isn't gonna work.
            raise NoMovesError('This piece cannot double advance in this position.')

        yield from plies


class ProhibitCastlingOverCheck(PlyProcessor):
    def __init__(self, game: Game, color: Color, from_pos: Vector2, to_pos: Vector2):
        self.game = game
        self.color = color
        self.from_pos = from_pos
        self.to_pos = to_pos

    def _threatened_across_range(self):
        for pos in board_range(self.from_pos, self.to_pos):
            state = self.game.next_state(
                self.color,
                Ply('Move', [MoveAction(self.from_pos, pos)])
            )

            if threatened(self.game, pos, [opposite(self.color)], state):
                raise NoMovesError('You cannot castle over check.')

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        for ply in plies:
            if ply.name != 'Castle':
                yield ply
            else:
                self._threatened_across_range()
                yield ply


class ProhibitEndingInCheck(PlyProcessor):
    def __init__(self, game: Game, color: Color):
        self.game = game
        self.color = color

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        for ply in plies:
            state = self.game.next_state(self.color, ply)

            king_position, king = next(find_pieces(state.board, King, self.color))

            if threatened(self.game, king_position, [opposite(self.color)], state):
                raise NoMovesError('That move leaves you in check.')
            else:
                yield ply


@dataclass
class Processor:
    processor: PlyProcessor
    stop_on_error: bool


class PlyProcessorChain(PlyProcessor):
    def __init__(self, ply_processors: List[Processor]):
        self.ply_processors = ply_processors

    def process(self, plies: Iterable[Ply]) -> Iterable[Ply]:
        for ply_processor in self.ply_processors:
            try:
                plies = ply_processor.processor.process(plies)
            except NoMovesError as error:
                if ply_processor.stop_on_error:
                    raise error

        return plies
