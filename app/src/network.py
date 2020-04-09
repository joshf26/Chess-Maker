import asyncio
import inspect
import json
import websockets

from dataclasses import dataclass
from itertools import islice
from typing import Dict, Callable, Awaitable, Union

from player import Player

ReplyCallable = Callable[[dict], Awaitable[None]]
ErrorCallable = Callable[[str], Awaitable[None]]


@dataclass
class Command:
    function: Callable
    parameters: Dict[str, type]


class Network:

    def __init__(self):
        self.commands: Dict[str, Command] = {}

        self.connections = set()
        self.socket_by_player = {}
        self.player_by_socket = {}

    def command(self, function: Callable):
        signature = inspect.signature(function)
        parameters = {name: parameter.annotation for name, parameter in islice(signature.parameters.items(), 2, None)}

        self.commands[function.__name__] = Command(function, parameters)

    def serve(self, port: int):
        print(f'Serving on port {port}...')

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(websockets.serve(self.server, '0.0.0.0', port))
        event_loop.run_forever()

    def send(self, to: Union[websockets.WebSocketServerProtocol, Player], data: dict):
        socket = self.socket_by_player[to] if isinstance(to, Player) else to
        socket.send(json.dumps(data))

    async def try_command(self, reply: ReplyCallable, error: ErrorCallable, data: dict):
        if 'command' not in data:
            await error('Command Not Specified')
            return

        if data['command'] not in self.commands:
            await error('Command Not Found')
            return

        parameters = self.commands[data['command']].parameters

        if parameters and 'parameters' not in data:
            await error(f'This command requires the following parameters: {", ".join(parameters.keys())}.')
            return

        payload = {}
        for parameter_name, parameter_type in parameters.items():
            if parameter_name not in data['parameters'] or type(data['parameters'][parameter_name]) is not parameter_type:
                await error(f'"{parameter_name}" parameter not specified.')
                return

            payload[parameter_name] = data['parameters'][parameter_name]

        await self.commands[data['command']].function(reply, error, **payload)

    async def server(self, websocket: websockets.WebSocketServerProtocol, path: str):
        self.connections.add(websocket)

        async def reply(reply_data: dict):
            await websocket.send(json.dumps(reply_data))

        async def error(message: str):
            await websocket.send(json.dumps({
                'error': message,
            }))

        try:
            async for raw_data in websocket:
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    await error('Invalid JSON')
                    continue

                await self.try_command(reply, error, data)

        finally:
            self.connections.remove(websocket)
