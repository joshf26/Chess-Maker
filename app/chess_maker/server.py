from typing import Dict

from color import Color
from game import Game
from game_subscribers import GameSubscribers
from network import Connection, Network
from pack import Pack
from piece import Direction
from vector2 import Vector2


class Server:

    def __init__(self, packs: Dict[str, Pack]):
        self.packs = packs

        self.games: Dict[str, Game] = {}
        self.subscribers = GameSubscribers()
        self.network = Network(self.on_disconnect)
        self._register_commands()

    def _register_commands(self) -> None:
        self.network.register_command('login', self.on_login)
        self.network.register_command('create_game', self.on_create_game)
        self.network.register_command('delete_game', self.on_delete_game)
        self.network.register_command('show_game', self.on_show_game)
        self.network.register_command('join_game', self.on_join_game)
        self.network.register_command('leave_game', self.on_leave_game)
        self.network.register_command('plies', self.on_plies)
        self.network.register_command('inventory_plies', self.on_inventory_plies)
        self.network.register_command('submit_ply', self.on_submit_ply)
        self.network.register_command('click_button', self.on_click_button)

    def _get_metadata(self, connection: Connection) -> dict:
        return {game_id: game.get_metadata(connection) for game_id, game in self.games.items()}

    async def _send_pack_data(self, connection: Connection) -> None:
        pack_data: Dict[str, dict] = {}

        for name, pack in self.packs.items():
            pack_data[name] = pack.to_json()

        await connection.run('update_pack_data', {
            'pack_data': pack_data,
        })

    async def _send_metadata_update_to_all(self) -> None:
        for connection in self.network.connections:
            await connection.run('update_game_metadata', {
                'game_metadata': self._get_metadata(connection),
            })

    def start(self, port: int) -> None:
        self.network.serve(port)

    async def on_disconnect(self, connection: Connection) -> None:
        change_made = False
        for game in self.games.values():
            if connection in game.subscribers:
                game.subscribers.remove_connection(connection)
                change_made = True

            if connection in game.players:
                game.players.remove_connection(connection)
                await game.send_update_to_subscribers()
                change_made = True

        if change_made:
            await self._send_metadata_update_to_all()

    async def on_login(self, connection: Connection, nickname: str) -> None:
        # Ensure there are no duplicate nicknames.
        nicknames = {connection.nickname for connection in self.network.connections}
        while nickname in nicknames:
            nickname += ' 2'

        print(f'{nickname} logged in!')
        connection.nickname = nickname

        await connection.run('set_nickname', {'nickname': nickname})
        await self._send_pack_data(connection)
        await connection.run('update_game_metadata', {
            'game_metadata': self._get_metadata(connection),
        })

    async def on_create_game(self, connection: Connection, name: str, pack: str, board: str) -> None:
        if pack not in self.packs:
            await connection.error('Package does not exist.')
            return

        controller_class = next(filter(lambda b: b.name == board, self.packs[pack].controllers), None)

        if controller_class is None:
            await connection.error('Controller does not exist.')
            return

        game = Game(name, connection, controller_class, self.network, self.subscribers)
        self.games[game.id] = game

        await self._send_metadata_update_to_all()

    async def on_delete_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            await connection.error('Game does not exist.')
            return

        if self.games[game_id].owner.nickname != connection.nickname:
            await connection.error('Only the owner of this game can delete it.')
            return

        del self.games[game_id]
        await self._send_metadata_update_to_all()

    async def on_show_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            await connection.error('Game does not exist.')
            return

        game = self.games[game_id]
        self.subscribers.set(game, connection)
        await connection.run('full_game_data', game.get_full_data(connection))

    async def on_join_game(self, connection: Connection, game_id: str, color: int) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection in game.players:
            await connection.error('Player is already in this game.')
            return

        color_object = next(filter(lambda x: x.value == color, Color.__iter__()), None)

        if color_object is None:
            await connection.error('Color does not exist.')
            return

        if color_object in game.players:
            await connection.error('That color is already taken in this game.')
            return

        game.add_player(connection, color_object)

        await self._send_metadata_update_to_all()
        await game.send_update_to_subscribers()

    async def on_leave_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            await connection.error('Player is not in this game.')
            return

        if connection in game.players:
            game.players.remove_connection(connection)

        await self._send_metadata_update_to_all()
        await game.send_update_to_subscribers()

    async def on_plies(
        self,
        connection: Connection,
        game_id: str,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        game = self.games[game_id]
        from_pos = Vector2(from_row, from_col)
        to_pos = Vector2(to_row, to_col)

        plies = game.get_plies(connection, from_pos, to_pos)
        await game.apply_or_offer_choices(from_pos, to_pos, plies, connection)

    async def on_inventory_plies(
        self,
        connection: Connection,
        game_id: str,
        pack_name: str,
        piece_name: str,
        piece_color: int,
        piece_direction: int,
        to_row: int,
        to_col: int,
    ) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        if piece_color < 0 or piece_color > 7 or piece_direction < 0 or piece_direction > 7:
            await connection.error('Invalid piece color or direction.')
            return

        game = self.games[game_id]

        selected_piece = next(filter(lambda piece: piece.name == piece_name, self.packs[pack_name].pieces), None)

        if selected_piece is None:
            await connection.error('Piece does not exist.')
            return

        to_pos = Vector2(to_row, to_col)
        inventory_plies = game.controller.inventory_plies(
            selected_piece(Color(piece_color), Direction(piece_direction)),
            to_pos,
        )

        await game.apply_or_offer_choices(Vector2(-1, -1), to_pos, inventory_plies, connection)

    async def on_submit_ply(
        self,
        connection: Connection,
        game_id: str,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        ply: dict,
    ) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        game = self.games[game_id]
        color = game.players.get_color(connection)
        plies = list(game.get_plies(connection, Vector2(from_row, from_col), Vector2(to_row, to_col)))
        dict_plies = [ply_data.to_json() for ply_data in plies]

        if ply not in dict_plies:
            await connection.error('Ply not available.')
            return

        ply_index = dict_plies.index(ply)

        await game.apply_ply(color, plies[ply_index])

    async def on_click_button(
        self,
        connection: Connection,
        game_id: str,
        button_id: str
    ) -> None:
        if game_id not in self.games:
            await connection.error('Game id does not exist.')
            return

        game = self.games[game_id]
        game.click_button(connection, button_id)
