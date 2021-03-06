from __future__ import annotations

import asyncio
import sys
import traceback
from asyncio import Task
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set, Dict, Type, Union, Callable, Awaitable
from uuid import uuid4

from .color import Color
from .controller import Controller
from .decorator import Decorator
from .game_subscribers import GameSubscribers
from .info_elements import InfoButton, InfoElement
from .inventory_item import InventoryItem
from .json_serializable import JsonSerializable
from .pack_util import get_pack
from .piece import Piece
from .actions import MoveAction, DestroyAction, CreateAction
from .ply import Ply, NoMovesError
from .vector2 import Vector2

if TYPE_CHECKING:
    from network import Network, Connection


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

    def get_color(self, connection: Connection) -> Optional[Color]:
        return self.connection_to_color.get(connection, None)

    def get_connection(self, color: Color) -> Optional[Connection]:
        return self.color_to_connection.get(color, None)


@dataclass
class GameData:
    history: List[GameState]
    board_size: Vector2
    colors: List[Color]

    @property
    def board(self) -> Dict[Vector2, Piece]:
        return self.history[-1].board


@dataclass
class GameState:
    board: Dict[Vector2, Piece]
    ply_color: Optional[Color]
    ply: Optional[Ply]


@dataclass
class WinnerData(JsonSerializable):
    colors: List[Color]
    reason: str

    def to_json(self) -> Union[dict, list]:
        return {
            'colors': [color.value for color in self.colors],
            'reason': self.reason,
        }


@dataclass
class ChatMessage(JsonSerializable):
    sender: Connection
    text: str

    def to_json(self) -> Union[dict, list]:
        return {
            'sender_id': self.sender.id,
            'text': self.text,
        }


class Game:

    def __init__(
        self,
        name: str,
        owner: Connection,
        controller_type: Type[Controller],
        controller_options: dict,
        network: Network,
        subscribers: GameSubscribers,
    ):
        self.name = name
        self.owner = owner
        self.network = network
        self.subscribers = subscribers

        self.id = str(uuid4())
        self.players = ColorConnections()
        self.controller = controller_type(self, controller_options)
        self.game_data = GameData([], self.controller.board_size, self.controller.colors)
        self.tasks: List[Task] = []

        self.decorator_layers: Dict[int, Dict[Vector2, Decorator]] = {}
        self.private_info_elements: Dict[Color, List[InfoElement]] = {color: [] for color in self.controller.colors}
        self.public_info_elements: List[InfoElement] = []
        self.inventories: Dict[Color, List[InventoryItem]] = {color: [] for color in self.controller.colors}
        self.winners: Optional[WinnerData] = None
        self.chat_messages: List[ChatMessage] = []

        self.active = True

        self._init_game()

    def __hash__(self):
        return hash(self.id)

    def _init_game(self) -> None:
        board: Dict[Vector2, Piece] = {}
        self.game_data.history.append(GameState(board, None, None))
        self.controller.init_board(board)

    def shutdown(self) -> None:
        if self.active:
            for task in self.tasks:
                task.cancel()

            self.active = False

    def get_metadata(self) -> dict:
        return {
            'display_name': self.name,
            'creator': self.owner.id,
            'controller_pack_id': get_pack(self.controller),
            'controller_id': self.controller.name,
            'players': {
                color.value: connection.id for color, connection in self.players.color_to_connection.items()
            },
        }

    def get_full_data(self, connection: Connection) -> dict:
        color = self.players.get_color(connection)
        inventory_items = self.inventories.get(color, [])

        pieces = [{
            'row': position.row,
            'col': position.col,
            'pack_id': get_pack(piece),  # TODO: Change to use piece.to_json().
            'piece_type_id': piece.__class__.__name__,
            'color': piece.color.value,
            'direction': piece.direction.value,
        } for position, piece in self.board.items()]
        decorators = {layer: [{
            'row': position.row,
            'col': position.col,
            'pack_id': get_pack(decorator),
            'decorator_type_id': decorator.__class__.__name__,
        } for position, decorator in decorators.items()] for layer, decorators in self.decorator_layers.items()}
        public_info_elements = [info_element.to_json() for info_element in self.public_info_elements]
        chat_messages = [chat_message.to_json() for chat_message in self.chat_messages]
        inventory = [inventory_item.to_json() for inventory_item in inventory_items]

        result = {
            'id': self.id,
            'pieces': pieces,
            'decorators': decorators,
            'public_info_elements': public_info_elements,
            'inventory_items': inventory,
            'chat_messages': chat_messages,
            'winners': None if self.winners is None else self.winners.to_json(),
        }

        if color is not None:
            result['private_info_elements'] = [
                info_element.to_json() for info_element in self.private_info_elements[color]
            ]

        return result

    def get_available_colors(self) -> Set[Color]:
        colors = set(self.controller.colors.copy())
        taken_colors = set(self.players.color_to_connection.keys())

        return colors - taken_colors

    def send_update_to_subscribers(self) -> None:
        for connection in self.subscribers.get_connections(self):
            connection.update_game_data(self)

    def update_decorator_layers(self, decorator_layers: Dict[int, Dict[Vector2, Decorator]]) -> None:
        self.decorator_layers.update(decorator_layers)

        for connection in self.subscribers.get_connections(self):
            connection.update_decorators(self, decorator_layers)

    def update_public_info(self, info_elements: List[InfoElement]) -> None:
        self.public_info_elements = info_elements

        for connection in self.subscribers.get_connections(self):
            connection.update_info_elements(self, info_elements, True)

    def update_private_info(self, color: Color, info_elements: List[InfoElement]) -> None:
        self.private_info_elements[color] = info_elements

        connection = self.players.get_connection(color)
        if connection is not None:
            connection.update_info_elements(self, info_elements, False)

    def update_inventory(self, color: Color, inventory_items: List[InventoryItem]) -> None:
        self.inventories[color] = inventory_items

        connection = self.players.get_connection(color)
        if connection is not None:
            connection.update_inventory_items(self, inventory_items)

    def send_error(self, color: Color, message: str) -> None:
        connection = self.players.get_connection(color)
        connection.show_error(message)

    def get_plies(self, connection: Connection, from_pos: Vector2, to_pos: Vector2) -> List[Ply]:
        if (
            self.winners is not None
            or from_pos not in self.board
            or to_pos.row < 0
            or to_pos.col < 0
            or to_pos.row >= self.controller.board_size.row
            or to_pos.col >= self.controller.board_size.col
        ):
            # Client must have sent stale data.
            return []

        color = self.players.get_color(connection)
        try:
            return list(self.controller.get_plies(color, from_pos, to_pos))
        except NoMovesError as error:
            self.send_error(color, str(error))
            return []

    def next_state(self, color: Optional[Color], ply: Optional[Ply]) -> GameState:
        board = deepcopy(self.board)

        if ply is not None:
            for action in ply.actions:
                if isinstance(action, MoveAction):
                    board[action.from_pos].moves += 1
                    board[action.to_pos] = board.pop(action.from_pos)

                elif isinstance(action, DestroyAction):
                    board.pop(action.pos)

                elif isinstance(action, CreateAction):
                    board[action.pos] = action.piece.copy()

        return GameState(board, color, ply)

    def apply_ply(self, color: Optional[Color], ply: Optional[Ply]) -> None:
        self.game_data.history.append(self.next_state(color, ply))

        # TODO: Investigate why ply is optional.
        if ply:
            for connection in self.subscribers.get_connections(self):
                connection.apply_ply(self, ply)

        self.controller.after_ply()

    def undo_ply(self) -> None:
        self.game_data.history.pop()
        self.send_update_to_subscribers()

    def apply_or_offer_choices(
        self,
        from_pos: Vector2,
        to_pos: Vector2,
        plies: List[Ply],
        connection: Connection,
    ) -> None:
        if len(plies) == 0:
            # No plies available.
            return

        if len(plies) == 1:
            # There is only one ply available, so just apply it immediately.
            self.apply_ply(self.players.get_color(connection), plies[0])
            return

        # There are multiple plies available, so present the user with a choice.
        connection.offer_plies(from_pos, to_pos, plies)

    def add_player(self, connection: Connection, color: Color) -> None:
        self.players.set(color, connection)

    def click_button(self, connection: Connection, button_id: str) -> None:
        color = self.players.get_color(connection)

        if color is None:
            return

        info_elements = self.public_info_elements + self.private_info_elements[color]
        for info_element in info_elements:
            if isinstance(info_element, InfoButton) and info_element.id == button_id:
                info_element.callback(color)
                break

    def winner(self, colors: List[Color], reason: str = None) -> None:
        self.winners = WinnerData(colors, reason)

        for connection in self.subscribers.get_connections(self):
            connection.update_winners(self)

        self.shutdown()

    def run_async(self, function: Callable[[], Awaitable]):
        async def do_function():
            # noinspection PyBroadException
            try:
                await function()
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)

        self.tasks.append(asyncio.create_task(do_function()))

    @property
    def board(self) -> Dict[Vector2, Piece]:
        return self.game_data.history[-1].board
