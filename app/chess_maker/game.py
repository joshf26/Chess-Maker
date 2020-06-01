from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set, Dict, Type, Generator, Union
from uuid import uuid4

from color import Color
from controller import Controller
from game_subscribers import GameSubscribers
from info_elements import InfoButton
from inventory_item import InventoryItem
from json_serializable import JsonSerializable
from piece import get_pack, Piece
from ply import Ply, MoveAction, DestroyAction, CreateAction
from vector2 import Vector2

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

    def get_color(self, connection: Connection):
        return self.connection_to_color.get(connection, None)

    def get_connection(self, color: Color):
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


class Game:

    def __init__(
        self,
        name: str,
        owner: Connection,
        controller_type: Type[Controller],
        network: Network,
        subscribers: GameSubscribers,
    ):
        self.name = name
        self.owner = owner
        self.network = network
        self.subscribers = subscribers

        self.id = str(uuid4())
        self.players = ColorConnections()
        self.controller = controller_type(self)
        self.game_data = GameData([], self.controller.board_size, self.controller.colors)
        self.winners: Optional[WinnerData] = None

        self._init_game()

    def __hash__(self):
        return hash(self.id)

    def _init_game(self) -> None:
        board: Dict[Vector2, Piece] = {}
        self.game_data.history.append(GameState(board, None, None))
        self.controller.init_board(board)

    def get_metadata(self, connection: Connection) -> dict:
        return {
            'name': self.name,
            'creator': self.owner.nickname,
            'pack': get_pack(self.controller),
            'board': self.controller.name,
            'players': [
                {
                    'color': color.value,
                    'nickname': connection.nickname,
                } for color, connection in self.players.color_to_connection.items()
            ],
            'total_players': [color.value for color in self.controller.colors],  # TODO: This should probably be sent with pack data.
            'playing_as': None if (color := self.players.get_color(connection)) is None else color.value,
        }

    def get_full_data(self, connection: Connection) -> dict:
        color = self.players.get_color(connection)
        inventory_items: List[InventoryItem] = [] if color is None else self.controller.get_inventory(color)

        pieces = [{
            'row': position.row,
            'col': position.col,
            'pack': get_pack(piece),
            'piece': piece.__class__.__name__,
            'color': piece.color.value,
            'direction': piece.direction.value,
        } for position, piece in self.board.items()]
        info = [info_element.to_json() for info_element in self.controller.get_info(color)]
        inventory = [dict(
            pack=get_pack(inventory_item.piece),
            quantity=inventory_item.quantity,
            **inventory_item.piece.to_json(),
        ) for inventory_item in inventory_items]

        return {
            'id': self.id,
            'pieces': pieces,
            'info': info,
            'inventory': inventory,
            'winners': None if self.winners is None else self.winners.to_json(),
        }

    def get_available_colors(self) -> Set[Color]:
        colors = set(self.controller.colors.copy())
        taken_colors = set(self.players.color_to_connection.keys())

        return colors - taken_colors

    def send_update(self, connection: Connection) -> None:
        game_data = self.get_full_data(connection)
        connection.run('full_game_data', game_data)

    def send_update_to_subscribers(self) -> None:
        for connection in self.subscribers.get_connections(self):
            self.send_update(connection)

    def get_plies(self, connection: Connection, from_pos: Vector2, to_pos: Vector2) -> Generator[Ply]:
        if (
            self.winners is not None
            or from_pos not in self.board
            or to_pos.row < 0
            or to_pos.col < 0
            or to_pos.row >= self.controller.board_size.row
            or to_pos.col >= self.controller.board_size.col
        ):
            # Client must have sent stale data.
            return

        color = self.players.get_color(connection)
        yield from self.controller.get_plies(color, from_pos, to_pos)

    def next_state(self, color: Color, ply: Ply) -> GameState:
        board = deepcopy(self.board)

        for action in ply.actions:
            if isinstance(action, MoveAction):
                board[action.from_pos].moves += 1
                board[action.to_pos] = board.pop(action.from_pos)

            elif isinstance(action, DestroyAction):
                board.pop(action.pos)

            elif isinstance(action, CreateAction):
                board[action.pos] = action.piece

        return GameState(board, color, ply)

    def apply_ply(self, color: Color, ply: Ply) -> None:
        self.game_data.history.append(self.next_state(color, ply))
        self.controller.after_ply()
        self.send_update_to_subscribers()

    def undo_ply(self) -> None:
        self.game_data.history.pop()
        self.send_update_to_subscribers()

    def apply_or_offer_choices(
        self,
        from_pos: Vector2,
        to_pos: Vector2,
        plies: Generator[Ply],
        connection: Connection,
    ) -> None:
        first = next(plies, None)
        if first is None:
            # No plies available.
            return

        second = next(plies, None)
        if second is None:
            # There is only one ply available, so just apply it immediately.
            self.apply_ply(self.players.get_color(connection), first)
            return

        full_plies = [first, second, *plies]

        # There are multiple plies available, so present the user with a choice.
        result = [ply.to_json() for ply in full_plies]

        connection.run('plies', {
            'from_row': from_pos.row,
            'from_col': from_pos.col,
            'to_row': to_pos.row,
            'to_col': to_pos.col,
            'plies': result,
        })

    def add_player(self, connection: Connection, color: Color) -> None:
        self.players.set(color, connection)

    def click_button(self, connection: Connection, button_id: str) -> None:
        color = self.players.get_color(connection)

        if color is None:
            return

        info_elements = self.controller.get_info(color)
        for info_element in info_elements:
            if isinstance(info_element, InfoButton) and info_element.id == button_id:
                info_element.callback(color)
                break

    def winner(self, colors: List[Color], reason: str = None) -> None:
        self.winners = WinnerData(colors, reason)

    @property
    def board(self) -> Dict[Vector2, Piece]:
        return self.game_data.history[-1].board
