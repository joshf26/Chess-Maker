from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Generator, Iterable
    from chessmaker import Ply
    from chessmaker.typings import Piece

from chessmaker import Color, Controller, Direction, Vector2
from chessmaker.info_elements import InfoText, InfoElement

from ..pieces import Bishop, King, Knight, Pawn, Queen, Rook
from ..helpers import (
    next_color, threatened, find_pieces, print_color, OFFSETS, opposite,
    CARDINALS, ORDINALS, get_piece_plies
)
from ..ply_processors import (
    OnlyPieceOwner, PlyProcessorChain, Processor, OnlyOnOwnTurn, AllowPawnPromotion,
    AllowPawnDoubleAdvance, ProhibitCastlingOverCheck, ProhibitEndingInCheck
)


class Chess(Controller):
    name = 'Chess'
    board_size = Vector2(8, 8)
    # TODO: Eventually have a structure like this:
    # teams = {
    #     'White': [('white', 'black')],
    #     'Black': [('black', 'white')],
    # }
    colors = [
        Color.WHITE,
        Color.BLACK,
    ]

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [7, 0]):
            board.update({
                Vector2(row, 0): Rook(color, direction),
                Vector2(row, 1): Knight(color, direction),
                Vector2(row, 2): Bishop(color, direction),
                Vector2(row, 3): Queen(color, direction),
                Vector2(row, 4): King(color, direction),
                Vector2(row, 5): Bishop(color, direction),
                Vector2(row, 6): Knight(color, direction),
                Vector2(row, 7): Rook(color, direction),
            })

        for color, direction, row in zip([Color.WHITE, Color.BLACK], [Direction.NORTH, Direction.SOUTH], [6, 1]):
            for col in range(8):
                board[Vector2(row, col)] = Pawn(color, direction)

        self._update_info()

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Iterable[Ply]:
        plies = get_piece_plies(self.game, from_pos, to_pos)

        chain = PlyProcessorChain([
            Processor(OnlyPieceOwner(self.game, color, from_pos), True),
            Processor(OnlyOnOwnTurn(self.game, color), True),
            Processor(AllowPawnPromotion(self.game, from_pos, to_pos), False),
            Processor(AllowPawnDoubleAdvance(self.game, color, from_pos, to_pos), True),
            Processor(ProhibitCastlingOverCheck(self.game, color, from_pos, to_pos), True),
            Processor(ProhibitEndingInCheck(self.game, color), True),
        ])

        plies = chain.process(plies)
        return plies

    def after_ply(self) -> None:
        # You cannot put yourself in checkmate, so we only need to check for the opposite color.
        color = next_color(self.game)
        king_position, king = next(find_pieces(self.game.board, King, color))

        if not self._has_legal_move(color):
            opposite_color = [opposite(color)]
            if threatened(self.game, king_position, opposite_color):
                self.game.winner(opposite_color, 'Checkmate')
            else:
                self.game.winner([], 'Stalemate')

        self._update_info()

    def _update_info(self) -> None:
        color = next_color(self.game)

        def generate() -> Generator[InfoElement]:
            yield InfoText(f'Current Turn: {print_color(color)}')

            # Check if their king is in check.
            king_position, king = next(find_pieces(self.game.board, King, color))
            if threatened(self.game, king_position, [opposite(color)]):
                yield InfoText(f'{print_color(color)} is in check!')

        self.game.update_public_info(list(generate()))

    def _is_legal(self, from_pos: Vector2, to_pos: Vector2) -> bool:
        if to_pos.row >= self.board_size.row or to_pos.row < 0 or to_pos.col >= self.board_size.col or to_pos.col < 0:
            return False

        piece = self.game.board[from_pos]
        plies = piece.get_plies(from_pos, to_pos, self.game.game_data)

        for ply in plies:
            state = self.game.next_state(piece.color, ply)

            king_position, king = next(find_pieces(state.board, King, piece.color))

            if not threatened(self.game, king_position, [opposite(piece.color)], state):
                return True

        return False

    def _has_legal_move(self, color: Color) -> bool:
        for pos, piece in find_pieces(self.game.board, color=color):
            if isinstance(piece, Pawn):
                if piece.direction == Direction.NORTH and (
                    self._is_legal(pos, pos + Vector2(0, -1))
                    or self._is_legal(pos, pos + Vector2(0, -2))
                    or self._is_legal(pos, pos + Vector2(1, -1))
                    or self._is_legal(pos, pos + Vector2(-1, -1))
                ):
                    return True

                if piece.direction == Direction.SOUTH and (
                    self._is_legal(pos, pos + Vector2(0, 1))
                    or self._is_legal(pos, pos + Vector2(0, 2))
                    or self._is_legal(pos, pos + Vector2(1, 1))
                    or self._is_legal(pos, pos + Vector2(-1, 1))
                ):
                    return True

            if isinstance(piece, Rook) or isinstance(piece, Queen):
                for direction in CARDINALS:
                    if self._is_legal(pos, pos + OFFSETS[direction]):
                        return True

            if isinstance(piece, Knight):
                if (
                    self._is_legal(pos, pos + Vector2(1, 2))
                    or self._is_legal(pos, pos + Vector2(2, 1))
                    or self._is_legal(pos, pos + Vector2(1, -2))
                    or self._is_legal(pos, pos + Vector2(2, -1))
                    or self._is_legal(pos, pos + Vector2(-1, 2))
                    or self._is_legal(pos, pos + Vector2(-2, 1))
                    or self._is_legal(pos, pos + Vector2(-1, -2))
                    or self._is_legal(pos, pos + Vector2(-2, -1))
                ):
                    return True

            if isinstance(piece, Bishop) or isinstance(piece, Queen):
                for direction in ORDINALS:
                    if self._is_legal(pos, pos + OFFSETS[direction]):
                        return True

            if isinstance(piece, King):
                for offset in OFFSETS.values():
                    if self._is_legal(pos, pos + offset):
                        return True

        return False
