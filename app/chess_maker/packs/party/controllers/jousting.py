from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, List, Dict, Generator

from color import Color
from controller import Controller
from info_elements import InfoButton, InfoText, InfoElement
from packs.standard.pieces.knight import Knight
from piece import Direction, Piece
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply
    from game import Game


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

    def __init__(self, game: Game):
        super().__init__(game)

        self.game_started = False
        self.countdown_started = False
        self.start_timer = 3

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

    def get_info(self, color: Color) -> List[InfoElement]:
        if self.countdown_started and not self.game_started:
            return [InfoText(f'<br>Game starting in {self.start_timer}')]

        return [] if self.game_started else [self.start_button]

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        if self.game_started:
            piece = self.game.board[from_pos]
            if color == piece.color:
                yield from piece.get_plies(from_pos, to_pos, self.game.game_data)

    def after_ply(self) -> None:
        if len(self.game.board) == 1:
            self.game.winner([list(self.game.board.values())[0].color], 'Last Knight Standing')

    def _start_game(self, color: Color):
        async def countdown():
            self._clear_unused()
            self.countdown_started = True
            self.game.send_update_to_subscribers()
            await asyncio.sleep(1)
            self.start_timer -= 1
            self.game.send_update_to_subscribers()
            await asyncio.sleep(1)
            self.start_timer -= 1
            self.game.send_update_to_subscribers()
            await asyncio.sleep(1)
            self.game_started = True
            self.game.send_update_to_subscribers()

        asyncio.create_task(countdown())

    def _clear_unused(self):
        for pos, piece in list(self.game.board.items()):
            if piece.color not in self.game.players:
                del self.game.board[pos]
