from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, List, Dict, Generator

from color import Color
from controller import Controller
from info_elements import InfoButton, InfoText, InfoElement
from packs.standard.helpers import get_color_info_texts
from packs.standard.pieces.knight import Knight
from piece import Direction, Piece
from vector2 import Vector2

if TYPE_CHECKING:
    from ply import Ply
    from game import Game
    from board import Board


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

        self.start_button = InfoButton('Start Game', self.start_game)

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
        result = get_color_info_texts(self.game)

        if self.countdown_started and not self.game_started:
            return result + [InfoText(f'<br>Game starting in {self.start_timer}')]

        return result if self.game_started else result + [self.start_button]

    def get_plies(self, color: Color, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        yield from self.game.board[from_pos].get_plies(from_pos, to_pos, self.game)

    async def start_game(self, color: Color):
        self.countdown_started = True
        await self.game.send_update_to_subscribers()
        await asyncio.sleep(1)
        self.start_timer -= 1
        await self.game.send_update_to_subscribers()
        await asyncio.sleep(1)
        self.start_timer -= 1
        await self.game.send_update_to_subscribers()
        await asyncio.sleep(1)
        self.game_started = True
        await self.game.send_update_to_subscribers()
