import asyncio
import inspect
import json
import uuid

import websockets

from dataclasses import dataclass
from itertools import islice
from typing import Dict, Callable, Set


class Connection:

    def __init__(self, socket: websockets.WebSocketServerProtocol):
        self.socket = socket
        self.id = uuid.uuid4()
        self.nickname = 'Player'

    async def run(self, command: str, parameters: dict):
        await self.socket.send(json.dumps({
            'command': command,
            'parameters': parameters,
        }))

    async def send(self, data: dict):
        await self.socket.send(json.dumps(data))

    async def error(self, message: str):
        await self.socket.send(json.dumps({
            'error': message,
        }))

    def __hash__(self):
        return hash(self.socket)


@dataclass
class Command:
    function: Callable
    parameters: Dict[str, type]


class Network:

    def __init__(self):
        self.commands: Dict[str, Command] = {}

        self.connections: Set[Connection] = set()
        self.socket_by_player = {}
        self.player_by_socket = {}

    def command(self):
        def inner(function: Callable):
            signature = inspect.signature(function)
            parameters = {
                name: parameter.annotation for name, parameter in islice(signature.parameters.items(), 1, None)
            }

            self.commands[function.__name__] = Command(function, parameters)

            return function

        return inner

    def serve(self, port: int):
        print(f'Serving on port {port}...')

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(websockets.serve(self.server, '0.0.0.0', port))
        event_loop.run_forever()

    async def try_command(self, connection: Connection, data: dict):
        if 'command' not in data:
            await connection.error('Command Not Specified')
            return

        if data['command'] not in self.commands:
            await connection.error('Command Not Found')
            return

        parameters = self.commands[data['command']].parameters

        if parameters and 'parameters' not in data:
            await connection.error(f'This command requires the following parameters: {", ".join(parameters.keys())}.')
            return

        payload = {}
        for parameter_name, parameter_type in parameters.items():
            if parameter_name not in data['parameters']:
                await connection.error(f'"{parameter_name}" parameter not specified.')
                return

            if type(data['parameters'][parameter_name]) is not parameter_type:
                await connection.error(f'"{parameter_name}" parameter needs to be of type {parameter_type.__name__}.')
                return

            payload[parameter_name] = data['parameters'][parameter_name]

        await self.commands[data['command']].function(connection, **payload)

    async def server(self, websocket: websockets.WebSocketServerProtocol, path: str):
        connection = Connection(websocket)
        self.connections.add(connection)

        try:
            async for raw_data in websocket:
                print(f'Received {raw_data}.')

                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    await connection.error('Invalid JSON')
                    continue

                await self.try_command(connection, data)

        finally:
            self.connections.remove(connection)
