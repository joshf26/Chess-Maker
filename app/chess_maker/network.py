import asyncio
import inspect
import json
import uuid
from dataclasses import dataclass
from itertools import islice
from typing import Dict, Callable, Set, Awaitable

import websockets


class Connection:

    def __init__(self, socket: websockets.WebSocketServerProtocol):
        self.socket = socket
        self.id = uuid.uuid4()
        self.nickname = 'Player'

    def run(self, command: str, parameters: dict):
        asyncio.create_task(self.socket.send(json.dumps({
            'command': command,
            'parameters': parameters,
        })))

    def error(self, message: str):
        asyncio.create_task(self.socket.send(json.dumps({
            'error': message,
        })))

    def __hash__(self):
        return hash(self.socket)


@dataclass
class Command:
    function: Callable
    parameters: Dict[str, type]


class Network:

    def __init__(self, on_disconnect: Callable[[Connection], Awaitable[None]]):
        self.on_disconnect = on_disconnect

        self.commands: Dict[str, Command] = {}

        self.connections: Set[Connection] = set()

    def register_command(self, command: str, callback: Callable) -> None:
        signature = inspect.signature(callback)
        parameters = {
            name: parameter.annotation for name, parameter in islice(signature.parameters.items(), 1, None)
        }

        self.commands[command] = Command(callback, parameters)

    def run_all(self, command: str, parameters: dict):
        for connection in self.connections:
            connection.run(command, parameters)

    def serve(self, port: int):
        print(f'Serving on port {port}...')

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(websockets.serve(self.server, '0.0.0.0', port))
        event_loop.run_forever()

    def try_command(self, connection: Connection, data: dict):
        if 'command' not in data:
            connection.error('Command Not Specified')
            return

        if data['command'] not in self.commands:
            connection.error('Command Not Found')
            return

        parameters = self.commands[data['command']].parameters

        if parameters and 'parameters' not in data:
            connection.error(f'This command requires the following parameters: {", ".join(parameters.keys())}.')
            return

        payload = {}
        for parameter_name, parameter_type in parameters.items():
            if parameter_name not in data['parameters']:
                connection.error(f'"{parameter_name}" parameter not specified.')
                return

            if type(data['parameters'][parameter_name]) is not parameter_type:
                connection.error(f'"{parameter_name}" parameter needs to be of type {parameter_type.__name__}.')
                return

            payload[parameter_name] = data['parameters'][parameter_name]

        self.commands[data['command']].function(connection, **payload)

    async def server(self, websocket: websockets.WebSocketServerProtocol, path: str):
        connection = Connection(websocket)
        self.connections.add(connection)

        try:
            async for raw_data in websocket:
                print(f'Received {raw_data}.')

                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    connection.error('Invalid JSON')
                    continue

                self.try_command(connection, data)
        except websockets.ConnectionClosedError:
            pass
        finally:
            print('Client disconnected.')
            self.connections.remove(connection)
            self.on_disconnect(connection)
