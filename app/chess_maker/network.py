from __future__ import annotations

import asyncio
import inspect
import json
import websockets

from uuid import uuid4
from dataclasses import dataclass
from itertools import islice
from typing import TYPE_CHECKING, Dict, Callable, Set, Iterable, Union

from json_serializable import JsonSerializable
from ply import Ply
from vector2 import Vector2

if TYPE_CHECKING:
    from game import Game
    from pack import Pack


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

    def show_error(self, message: str) -> None:
        self._run('show_error', {
            'message': message,
        })

    def offer_plies(self, from_pos: Vector2, to_pos: Vector2, plies: Iterable[Ply]) -> None:
        self._run('plies', {
            'from_row': from_pos.row,
            'from_col': from_pos.col,
            'to_row': to_pos.row,
            'to_col': to_pos.col,
            'plies': [ply.to_json() for ply in plies],
        })

    def receive_server_chat_message(self, text: str, sender: Connection, game: Game = None) -> None:
        self._run('receive_server_chat_message', {
            'text': text,
            'sender_id': sender.id,
            'game_id': game.id if game else 'server',
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

    def __init__(self, on_disconnect: Callable[[Connection], None]):
        self.on_disconnect = on_disconnect

        self.commands: Dict[str, Command] = {}

        self.connection: Set[Connection] = set()

    @property
    def active_connections(self) -> Iterable[Connection]:
        return filter(lambda connection: connection.active, self.connection)

    def register_command(self, command: str, callback: Callable) -> None:
        signature = inspect.signature(callback)
        parameters = {
            name: parameter.annotation for name, parameter in islice(signature.parameters.items(), 1, None)
        }

        self.commands[command] = Command(callback, parameters)

    def all_update_players(self) -> None:
        for connection in self.active_connections:
            connection.update_players(self.connection)

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
        connection = Connection(websocket)
        self.connection.add(connection)

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
            print('Client disconnected.')
            connection.active = False
            self.on_disconnect(connection)
