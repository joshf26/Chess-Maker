from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set, Tuple, Dict, Type
from uuid import uuid4

from ply import Ply, MoveAction, DestroyAction, ply_to_dicts, CreateAction
from color import Color
from board import InfoButton, Vector2

if TYPE_CHECKING:
    from network import Network, Connection
    from board import Board, Tiles


@dataclass
class HistoryEvent:
    color: Color
    tiles: Tiles
    ply: Ply


class ColorConnections:

    def __init__(self):
        self.color_to_connection: Dict[Color, Connection] = {}
        self.connection_to_color: Dict[Connection, Color] = {}

    def __len__(self):
        return len(self.color_to_connection)

    def __contains__(self, item):
        if isinstance(item, Color):
            return item in self.color_to_connection
        else:
            return item in self.connection_to_color

    def set(self, color: Color, connection: Connection):
        self.color_to_connection[color] = connection
        self.connection_to_color[connection] = color

    def remove_connection(self, connection: Connection):
        color = self.connection_to_color[connection]

        del self.connection_to_color[connection]
        del self.color_to_connection[color]

    def get_color(self, connection: Connection):
        return self.connection_to_color.get(connection, None)

    def get_connection(self, color: Color):
        return self.color_to_connection.get(color, None)


class Game:

    def __init__(self, name: str, owner: Connection, board_class: Type[Board], network: Network):
        self.name = name
        self.owner = owner
        self.network = network

        self.id = str(uuid4())

        self.subscribers: Set[Connection] = set()
        self.players = ColorConnections()

        self.plies: List[Ply] = []
        self.history: List[HistoryEvent] = []

        self.board = board_class(self)

    def get_available_colors(self) -> Set[Color]:
        colors = set(self.board.colors.copy())
        taken_colors = set(self.players.color_to_connection.keys())

        return colors - taken_colors

    def get_full_data(self, connection: Connection) -> dict:
        color = self.players.get_color(connection)

        inventory = [] if color is None else self.board.get_inventory(color)

        # TODO: Maybe make this nested dictionaries instead of strings.
        return {
            'tiles': [{
                'row': position.row,
                'col': position.col,
                'pack': piece.__module__.split('.')[1],  # TODO: Extract into function?
                'piece': piece.__class__.__name__,
                'color': piece.color.value,
                'direction': piece.direction.value,
            } for position, piece in self.board.tiles.items()],
            'info': [info_element.to_dict() for info_element in self.board.get_info(color)],
            'inventory': [dict(pack=piece[0].__module__.split('.')[1], **piece[0].to_dict(), quantity=piece[1]) for piece in inventory]
        }

    async def send_update(self, connection: Connection):
        game_data = self.get_full_data(connection)
        game_data['id'] = self.id
        await connection.run('full_game_data', game_data)

    async def send_update_to_subscribers(self):
        for connection in self.subscribers:
            await self.send_update(connection)

    # TODO: Make this a generator... any maybe inventory_plies too.
    def get_plies(self, from_pos: Vector2, to_pos: Vector2) -> List[Tuple[str, Ply]]:
        if (
            from_pos not in self.board.tiles
            or to_pos.row < 0
            or to_pos.col < 0
            or to_pos.row >= self.board.size[0]
            or to_pos.col >= self.board.size[1]
        ):
            # Client must have sent stale data.
            return []

        piece_plies = self.board.tiles[from_pos].ply_types(from_pos, to_pos, self)

        return self.board.process_plies(piece_plies, from_pos, to_pos)

    async def apply_or_offer_choices(self, from_pos: Vector2, to_pos: Vector2, plies: List[Tuple[str, Ply]], connection: Connection):
        if len(plies) == 1:
            # There is only one ply available, so just apply it immediately.
            await self.apply_ply(plies[0][1])
        elif len(plies) > 1:
            # There are multiple plies available, so present the user with a choice.
            result = [{
                'name': ply[0],
                'actions': ply_to_dicts(ply[1])
            } for ply in plies]

            await connection.run('plies', {
                'from_row': from_pos.row,
                'from_col': from_pos.col,
                'to_row': to_pos.row,
                'to_col': to_pos.col,
                'plies': result,
            })

    async def apply_ply(self, ply: Ply):
        self.history.append(HistoryEvent(self.current_color(), self.board.tiles.copy(), ply))

        for action in ply:
            if isinstance(action, MoveAction):
                self.board.tiles[action.from_pos].moves += 1
                self.board.tiles[action.to_pos] = self.board.tiles.pop(action.from_pos)

            elif isinstance(action, DestroyAction):
                self.board.tiles.pop(action.pos)

            elif isinstance(action, CreateAction):
                self.board.tiles[action.pos] = action.piece

        await self.send_update_to_subscribers()

    def add_player(self, connection: Connection, color: Color):
        self.players.set(color, connection)

    # TODO: This should not be part of the Game class.
    def current_color(self) -> Color:
        if len(self.history) == 0:
            # TODO: Board should be validated at some point to ensure there is at least one color.
            return self.board.colors[0]

        color_index = self.board.colors.index(self.history[-1].color) + 1
        return self.board.colors[color_index % len(self.board.colors)]

    def n_event_by_color(self, color: Color, n: int, reverse: bool = False) -> Optional[HistoryEvent]:
        assert n > 0, 'n must be greater than 0'

        counter = 0
        for history_event in reversed(self.history) if reverse else self.history:
            if history_event.color == color:
                counter += 1
                if counter == n:
                    return history_event

        return None

    def click_button(self, connection: Connection, button_id: str):
        color = self.players.get_color(connection)

        if color is None:
            return

        info_elements = self.board.get_info(color)
        for info_element in info_elements:
            if isinstance(info_element, InfoButton) and info_element.id == button_id:
                asyncio.create_task(info_element.callback(color))
                break
