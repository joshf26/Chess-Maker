from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Tuple, List

from board import Board, InfoElement, InfoButton, InfoText
from color import Color
from packs.standard.helpers import get_color_info_texts
from packs.standard.pieces.knight import Knight
from piece import Direction

if TYPE_CHECKING:
    from ply import Ply
    from game import Game
    from board import Tiles


class Jousting(Board):
    name = 'Jousting'
    size = (8, 8)
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

    def init_board(self) -> Tiles:
        board: Tiles = {
            (0, 2): Knight(Color.WHITE, Direction.NORTH),
            (0, 5): Knight(Color.BLACK, Direction.NORTH),
            (2, 7): Knight(Color.RED, Direction.NORTH),
            (5, 7): Knight(Color.ORANGE, Direction.NORTH),
            (7, 5): Knight(Color.YELLOW, Direction.NORTH),
            (7, 2): Knight(Color.GREEN, Direction.NORTH),
            (5, 0): Knight(Color.BLUE, Direction.NORTH),
            (2, 0): Knight(Color.PURPLE, Direction.NORTH),
        }

        return board

    async def countdown(self):
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

    def start_game(self):
        asyncio.create_task(self.countdown())

    def get_info(self, color: Color) -> List[InfoElement]:
        result = get_color_info_texts(self.game, trailing_space=not self.game_started)

        if self.countdown_started and not self.game_started:
            return result + [InfoText(f'Game starting in {self.start_timer}')]

        return result if self.game_started else result + [self.start_button]

    def process_plies(
        self,
        plies: List[Ply],
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> List[Ply]:
        return plies if self.game_started else []
