import asyncio
import json
from typing import Dict, Callable, Awaitable

import websockets

ReplyCallable = Callable[[dict], Awaitable[None]]


class Network:

    def __init__(self):
        self.commands: Dict[str, Callable[[ReplyCallable, dict], Awaitable[None]]] = {}

    def serve(self, port: int):
        print(f'Serving on port {port}...')

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(websockets.serve(self.server, '0.0.0.0', port))
        event_loop.run_forever()

    async def server(self, websocket: websockets.WebSocketServerProtocol, path: str):
        async def reply(reply_data: Dict[str, any]):
            await websocket.send(json.dumps(reply_data))

        async def reply_error(error: str):
            await websocket.send(json.dumps({
                'error': error,
            }))

        raw_data = await websocket.recv()

        print(raw_data)

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            await reply_error('Invalid JSON')
            return

        if 'command' not in data:
            await reply_error('Command Not Specified')
            return

        if data['command'] not in self.commands:
            await reply_error('Command Not Found')
            return

        await self.commands[data['command']](reply, {})
