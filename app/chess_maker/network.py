from __future__ import annotations

import asyncio
import inspect
import json
from urllib.parse import parse_qs

import websockets

from uuid import uuid4
from dataclasses import dataclass
from itertools import islice
from typing import TYPE_CHECKING, Dict, Callable, Set, Iterable, Union, Tuple

from json_serializable import JsonSerializable
from pack_util import get_pack
from ply import Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from game import Game
    from pack import Pack


def parse_path(path: str) -> Tuple[str]:
    # Remove the leading slash.
    path = path[1:]

    query = parse_qs(path)
    return query['display_name'][0],


class Connection(JsonSerializable):

    def __init__(self, socket: websockets.WebSocketServerProtocol):
        self.socket = socket
        self.id = str(uuid4())
        self.display_name = 'Player'
        self.active = True

    def __str__(self):
        return f'Connection({self.id}, {self.display_name})'

    def __hash__(self):
        return hash(self.socket)

    def _run(self, command: str, parameters: dict) -> None:
        asyncio.create_task(self.socket.send(json.dumps({
            'command': command,
            'parameters': parameters,
        })))

    def set_player(self) -> None:
        self._run('set_player', {
            'id': self.id,
        })

    def focus_game(self, game: Game) -> None:
        self._run('focus_game', {
            'game_id': game.id,
        })

    def update_pack_data(self, packs: Dict[str, Pack]) -> None:
        self._run('update_pack_data', {
            'packs': {name: pack.to_json() for name, pack in packs.items()},
        })

    def update_players(self, players: Iterable[Connection]) -> None:
        self._run('update_players', {
            'players': {connection.id: connection.to_json() for connection in players},
        })

    def update_game_metadata(self, games: Dict[str, Game]) -> None:
        self._run('update_game_metadata', {
            'game_metadata': {game_id: game.get_metadata() for game_id, game in games.items()},
        })

    def update_game_data(self, game: Game) -> None:
        self._run('update_game_data', game.get_full_data(self))

    def update_decorators(self, game: Game) -> None:
        self._run('update_decorators', {
            'game_id': game.id,
            'decorators': {
                layer: [{
                    'row': pos.row,
                    'col': pos.col,
                    'pack_id': get_pack(decorator),
                    'decorator_type_id': decorator.__class__.__name__,
                } for pos, decorator in decorators.items()] for layer, decorators in game.decorator_layers.items()
            },
        })

    def update_info_elements(self, game: Game, is_public: bool) -> None:
        color = game.players.get_color(self)
        info_elements = game.public_info_elements.items if is_public else game.private_info_elements[color].items

        self._run('update_info_elements', {
            'game_id': game.id,
            'info_elements': [info_element.to_json() for info_element in info_elements],
            'is_public': is_public,
        })

    def update_inventory_items(self, game: Game) -> None:
        color = game.players.get_color(self)

        self._run('update_inventory_items', {
            'game_id': game.id,
            'inventory_items': [inventory_item.to_json() for inventory_item in game.inventories[color].items]
        })

    def apply_ply(self, game: Game, ply: Ply) -> None:
        self._run('apply_ply', {
            'game_id': game.id,
            'ply': ply.to_json(),
        })

    def update_winners(self, game: Game) -> None:
        self._run('update_winners', {
            'game_id': game.id,
            **game.winners.to_json(),
        })

    def receive_game_chat_message(self, game: Game, sender: Connection, text: str) -> None:
        self._run('receive_game_chat_message', {
            'game_id': game.id,
            'sender_id': sender.id,
            'text': text,
        })

    def receive_server_chat_message(self, text: str, sender: Connection, game: Game = None) -> None:
        self._run('receive_server_chat_message', {
            'text': text,
            'sender_id': sender.id,
            'game_id': game.id if game else 'server',
        })

    def show_error(self, message: str) -> None:
        self._run('show_error', {
            'message': message,
        })

    def offer_plies(self, from_pos: Vector2, to_pos: Vector2, plies: Iterable[Ply]) -> None:
        self._run('offer_plies', {
            'from_row': from_pos.row,
            'from_col': from_pos.col,
            'to_row': to_pos.row,
            'to_col': to_pos.col,
            'plies': [ply.to_json() for ply in plies],
        })

    def to_json(self) -> Union[dict, list]:
        return {
            'display_name': self.display_name,
            'active': self.active,
        }


@dataclass
class Command:
    function: Callable
    parameters: Dict[str, type]


class Network:

    def __init__(self, on_connect: Callable[[Connection], None], on_disconnect: Callable[[Connection], None]):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

        self.commands: Dict[str, Command] = {}

        self.connections: Set[Connection] = set()

    @property
    def active_connections(self) -> Iterable[Connection]:
        return filter(lambda connection: connection.active, self.connections)

    def register_command(self, command: str, callback: Callable) -> None:
        signature = inspect.signature(callback)
        parameters = {
            name: parameter.annotation for name, parameter in islice(signature.parameters.items(), 1, None)
        }

        self.commands[command] = Command(callback, parameters)

    def all_update_players(self) -> None:
        for connection in self.active_connections:
            connection.update_players(self.connections)

    def all_update_game_metadata(self, games: Dict[str, Game]) -> None:
        for connection in self.active_connections:
            connection.update_game_metadata(games)

    def serve(self, port: int):
        print(f'Serving on port {port}...')

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(websockets.serve(self.server, '0.0.0.0', port))
        event_loop.run_forever()

    def try_command(self, connection: Connection, data: dict):
        if 'command' not in data:
            connection.show_error('Command Not Specified')
            return

        if data['command'] not in self.commands:
            connection.show_error('Command Not Found')
            return

        parameters = self.commands[data['command']].parameters

        if parameters and 'parameters' not in data:
            connection.show_error(f'This command requires the following parameters: {", ".join(parameters.keys())}.')
            return

        payload = {}
        for parameter_name, parameter_type in parameters.items():
            if parameter_name not in data['parameters']:
                connection.show_error(f'"{parameter_name}" parameter not specified.')
                return

            if type(data['parameters'][parameter_name]) is not parameter_type:
                connection.show_error(f'"{parameter_name}" parameter needs to be of type {parameter_type.__name__}.')
                return

            payload[parameter_name] = data['parameters'][parameter_name]

        self.commands[data['command']].function(connection, **payload)

    async def server(self, websocket: websockets.WebSocketServerProtocol, path: str):
        display_name, = parse_path(path)

        while True:
            similar_player = next(filter(
                lambda other_player: other_player.display_name == display_name,
                self.connections,
            ), None)

            if similar_player is None:
                # This is a new user.
                connection = Connection(websocket)
                connection.display_name = display_name
                self.connections.add(connection)
                break

            if not similar_player.active:
                # The user has logged in before. Reuse their old player.
                similar_player.socket = websocket
                similar_player.active = True
                connection = similar_player
                break

            # Ensure there are no duplicate display names.
            display_name += ' (2)'

        self.on_connect(connection)

        try:
            async for raw_data in websocket:
                print(f'Received {raw_data}.')

                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    connection.show_error('Invalid JSON')
                    continue

                self.try_command(connection, data)
        except websockets.ConnectionClosedError:
            pass
        finally:
            print(f'{connection.display_name} disconnected.')
            connection.active = False
            self.on_disconnect(connection)
