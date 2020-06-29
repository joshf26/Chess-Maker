from __future__ import annotations

from typing import Generator, List, Dict, Optional

from color import Color
from controller import Controller
from inventory_item import InventoryItem
from packs.standard.controllers.chess import Chess
from packs.standard.helpers import next_color
from piece import Piece, Direction
from ply import Ply, CreateAction, DestroyAction
from vector2 import Vector2


class CrazyHouse(Chess, Controller):
    name = 'Crazy House'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inventories: Dict[Color, List[InventoryItem]] = {
            Color.WHITE: [],
            Color.BLACK: [],
        }

    def get_inventory(self, color: Color) -> List[InventoryItem]:
        return self.inventories[color]

    def get_inventory_plies(self, color: Color, piece: Piece, pos: Vector2) -> Generator[Ply]:
        # Make sure it is their turn.
        if color != next_color(self.game):
            self.game.send_error(color, 'It is not your turn.')
            return

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

            inventory_item = self._get_existing_inventory_item(state.ply_color, piece)
            if not inventory_item:
                inventory_item = InventoryItem(piece, '0')
                self.inventories[state.ply_color].append(inventory_item)

            inventory_item.label = str(int(inventory_item.label) + 1)
        else:
            places = filter(lambda action: isinstance(action, CreateAction), state.ply.actions)

            for place in places:
                inventory_item = self._get_existing_inventory_item(state.ply_color, place.piece)
                inventory_item.label = str(int(inventory_item.label) - 1)

                if inventory_item.label == '0':
                    self.inventories[state.ply_color].remove(inventory_item)

    def _get_existing_inventory_item(self, color: Color, piece: Piece) -> Optional[InventoryItem]:
        for inventory_item in self.inventories[color]:
            if (
                type(inventory_item.piece) == type(piece)
                and inventory_item.piece.color == piece.color
                and inventory_item.piece.direction == piece.direction
            ):
                return inventory_item
