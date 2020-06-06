from __future__ import annotations

from typing import Generator, List, Dict

from color import Color
from controller import Controller
from game import Game
from inventory_item import InventoryItem
from packs.standard.controllers.chess import Chess
from piece import Piece, Direction
from ply import Ply, CreateAction, DestroyAction
from vector2 import Vector2


class CrazyHouse(Chess, Controller):
    name = 'Crazy House'

    def __init__(self, game: Game):
        super().__init__(game)

        self.inventories: Dict[Color, List[InventoryItem]] = {
            Color.WHITE: [],
            Color.BLACK: [],
        }

    def get_inventory(self, color: Color) -> List[InventoryItem]:
        return self.inventories[color]

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        yield Ply('Create', [CreateAction(piece, pos)])

    def after_ply(self) -> None:
        super().after_ply()

        if len(self.game.game_data.history) < 2:
            return

        state = self.game.game_data.history[-1]
        prev_state = self.game.game_data.history[-2]

        captures = filter(lambda action: isinstance(action, DestroyAction), state.ply.actions)

        for capture in captures:
            piece = prev_state.board[capture.pos].__class__(
                state.ply_color,
                Direction.NORTH if state.ply_color == Color.WHITE else Direction.SOUTH,
            )
            self.inventories[state.ply_color].append(InventoryItem(piece, 1))
