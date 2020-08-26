from __future__ import annotations
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Dict, Generator

from color import Color
from controller import Controller
from info_elements import InfoButton, InfoText
from option import IntOption
from packs.standard.pieces.knight import Knight
from piece import Direction, Piece
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply


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
        'Game Start Timer': IntOption(3, 0)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_started = False
        self.start_button = InfoButton('Start Game', self._start_game)

    def init_board(self, board: Dict[Vector2, Piece]) -> None:
        board[Vector2(0, 2)] = Knight(Color.WHITE, Direction.NORTH)
        board[Vector2(0, 5)] = Knight(Color.BLACK, Direction.NORTH)
        board[Vector2(2, 7)] = Knight(Color.RED, Direction.NORTH)
        board[Vector2(5, 7)] = Knight(Color.ORANGE, Direction.NORTH)
        board[Vector2(7, 5)] = Knight(Color.YELLOW, Direction.NORTH)
        board[Vector2(7, 2)] = Knight(Color.GREEN, Direction.NORTH)
        board[Vector2(5, 0)] = Knight(Color.BLUE, Direction.NORTH)
        board[Vector2(2, 0)] = Knight(Color.PURPLE, Direction.NORTH)

        with self.game.public_info_elements as info:
            info.append(self.start_button)

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        if self.game_started:
            piece = self.game.board[from_pos]
            if color == piece.color:
                yield from piece.get_plies(from_pos, to_pos, self.game.game_data)
        else:
            self.game.send_error(color, 'The game has not started yet.')

    def after_ply(self) -> None:
        if len(self.game.board) == 1:
            self.game.winner([list(self.game.board.values())[0].color], 'Last Knight Standing')

    def _start_game(self, color: Color):
        async def countdown():
            self._clear_unused()

            # Remove the start game button and add the countdown timer element.
            with self.game.public_info_elements as info:
                info.remove(self.start_button)
                info.append(InfoText(''))

            # Tick the countdown the set number of times.
            for timer in range(self.options['Game Start Timer'].value, 0, -1):
                with self.game.public_info_elements as info:
                    info[0].text = f'Game starting in {timer}'

                await asyncio.sleep(1)

            # Remove the countdown.
            with self.game.public_info_elements as info:
                del info[0]

            self.game_started = True

        asyncio.create_task(countdown())

    def _clear_unused(self):
        for pos, piece in list(self.game.board.items()):
            if piece.color not in self.game.players:
                del self.game.board[pos]
