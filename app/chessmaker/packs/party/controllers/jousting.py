from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Iterable
    from chessmaker.typings import Piece

import asyncio

from chessmaker import Color, Controller, Direction, Ply, Vector2
from chessmaker.info_elements import InfoButton, InfoText
from chessmaker.actions import DestroyAction
from chessmaker.options import IntOption
from ....packs.standard.pieces import Knight


class Jousting(Controller):
    name = 'Jousting'
    board_size = Vector2(8, 8)
    colors = [
        Color.WHITE,
        Color.BLACK,
        Color.RED,
        Color.ORANGE,
        Color.YELLOW,
        Color.GREEN,
        Color.BLUE,
        Color.PURPLE,
    ]
    options = {
        'Game Start Timer': IntOption(3, 0),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_started = False

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        board.update({
            Vector2(0, 2): Knight(Color.WHITE, Direction.NORTH),
            Vector2(0, 5): Knight(Color.BLACK, Direction.NORTH),
            Vector2(2, 7): Knight(Color.RED, Direction.NORTH),
            Vector2(5, 7): Knight(Color.ORANGE, Direction.NORTH),
            Vector2(7, 5): Knight(Color.YELLOW, Direction.NORTH),
            Vector2(7, 2): Knight(Color.GREEN, Direction.NORTH),
            Vector2(5, 0): Knight(Color.BLUE, Direction.NORTH),
            Vector2(2, 0): Knight(Color.PURPLE, Direction.NORTH),
        })

        self.game.update_public_info([InfoButton('Start Game', self._start_game)])

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Iterable[Ply]:
        if self.game_started:
            piece = self.game.board[from_pos]
            if color == piece.color:
                yield from piece.get_plies(from_pos, to_pos, self.game.game_data)
            else:
                self.game.send_error(color, 'That is not your piece.')
        else:
            self.game.send_error(color, 'The game has not started yet.')

    def after_ply(self) -> None:
        if len(self.game.board) == 1:
            self.game.winner([list(self.game.board.values())[0].color], 'Last Knight Standing')

    def _start_game(self, color: Color):
        async def countdown():
            self.game.apply_ply(None, Ply('Clear Board', [
                DestroyAction(pos)
                for pos in self.game.board.keys()
                if self.game.board[pos].color not in self.game.players
            ]))

            # Tick the countdown the set number of times.
            for timer in range(self.options['Game Start Timer'].value, 0, -1):
                self.game.update_public_info([InfoText(f'Game starting in {timer}')])
                await asyncio.sleep(1)

            # Remove the countdown.
            self.game.update_public_info([])

            self.game_started = True

        self.game.run_async(countdown)
