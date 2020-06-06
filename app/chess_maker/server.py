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

    def _get_game_metadata(self, connection: Connection) -> dict:
        return {game_id: game.get_metadata(connection) for game_id, game in self.games.items()}

    def _get_players(self):
        return [connection.nickname for connection in self.network.connections]

    def _send_pack_data(self, connection: Connection) -> None:
        pack_data: Dict[str, dict] = {}

        for name, pack in self.packs.items():
            pack_data[name] = pack.to_json()

        connection.run('update_pack_data', {
            'pack_data': pack_data,
        })

    def _send_metadata_update(self, connection: Connection) -> None:
        connection.run('update_metadata', {
            'game_metadata': self._get_game_metadata(connection),
            'players': self._get_players(),
        })

    def _send_metadata_update_to_all(self) -> None:
        for connection in self.network.connections:
            self._send_metadata_update(connection)

    def start(self, port: int) -> None:
        self.network.serve(port)

    def on_disconnect(self, connection: Connection) -> None:
        change_made = False
        for game in self.games.values():
            if connection in game.subscribers:
                game.subscribers.remove_connection(connection)
                change_made = True

            if connection in game.players:
                game.players.remove_connection(connection)
                game.send_update_to_subscribers()
                change_made = True

        if change_made:
            self._send_metadata_update_to_all()

    def on_login(self, connection: Connection, nickname: str) -> None:
        # Ensure there are no duplicate nicknames.
        nicknames = {connection.nickname for connection in self.network.connections}
        while nickname in nicknames:
            nickname += ' 2'

        print(f'{nickname} logged in!')
        connection.nickname = nickname

        connection.run('set_nickname', {'nickname': nickname})
        self._send_pack_data(connection)
        self._send_metadata_update_to_all()

    def on_create_game(self, connection: Connection, name: str, pack: str, board: str, options: dict) -> None:
        if pack not in self.packs:
            connection.error('Package does not exist.')
            return

        controller_class = next(filter(lambda b: b.name == board, self.packs[pack].controllers), None)

        if controller_class is None:
            connection.error('Controller does not exist.')
            return

        if options.keys() != controller_class.options.keys():  # TODO: Improve error reporting and add type checking.
            connection.error('Options not supplied successfully.')
            return

        game = Game(name, connection, controller_class, options, self.network, self.subscribers)
        self.games[game.id] = game

        self._send_metadata_update_to_all()
        connection.run('focus_game', {'game_id': game.id})

    def on_delete_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.error('Game does not exist.')
            return

        if self.games[game_id].owner.nickname != connection.nickname:
            connection.error('Only the owner of this game can delete it.')
            return

        del self.games[game_id]
        self._send_metadata_update_to_all()

    def on_show_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.error('Game does not exist.')
            return

        game = self.games[game_id]
        self.subscribers.set(game, connection)
        connection.run('full_game_data', game.get_full_data(connection))

    def on_join_game(self, connection: Connection, game_id: str, color: int) -> None:
        if game_id not in self.games:
            connection.error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection in game.players:
            connection.error('Player is already in this game.')
            return

        color_object = next(filter(lambda x: x.value == color, Color.__iter__()), None)

        if color_object is None:
            connection.error('Color does not exist.')
            return

        if color_object in game.players:
            connection.error('That color is already taken in this game.')
            return

        game.add_player(connection, color_object)

        self._send_metadata_update_to_all()
        game.send_update_to_subscribers()

    def on_leave_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            connection.error('Player is not in this game.')
            return

        if connection in game.players:
            game.players.remove_connection(connection)

        self._send_metadata_update_to_all()
        game.send_update_to_subscribers()

    def on_plies(
        self,
        connection: Connection,
        game_id: str,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> None:
        if game_id not in self.games:
            connection.error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            connection.error('Player is not in this game.')
            return

        from_pos = Vector2(from_row, from_col)
        to_pos = Vector2(to_row, to_col)

        plies = game.get_plies(connection, from_pos, to_pos)
        game.apply_or_offer_choices(from_pos, to_pos, plies, connection)

    def on_inventory_plies(
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
            connection.error('Game id does not exist.')
            return

        if piece_color < 0 or piece_color > 7 or piece_direction < 0 or piece_direction > 7:
            connection.error('Invalid piece color or direction.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            connection.error('Player is not in this game.')
            return

        selected_piece = next(filter(lambda piece: piece.name == piece_name, self.packs[pack_name].pieces), None)

        if selected_piece is None:
            connection.error('Piece does not exist.')
            return

        to_pos = Vector2(to_row, to_col)
        color = Color(piece_color)
        inventory_plies = game.controller.get_inventory_plies(
            color,
            selected_piece(color, Direction(piece_direction)),
            to_pos,
        )

        game.apply_or_offer_choices(Vector2(-1, -1), to_pos, inventory_plies, connection)

    def on_submit_ply(
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
            connection.error('Game id does not exist.')
            return

        game = self.games[game_id]
        color = game.players.get_color(connection)
        plies = list(game.get_plies(connection, Vector2(from_row, from_col), Vector2(to_row, to_col)))
        dict_plies = [ply_data.to_json() for ply_data in plies]

        if ply not in dict_plies:
            connection.error('Ply not available.')
            return

        ply_index = dict_plies.index(ply)

        game.apply_ply(color, plies[ply_index])

    def on_click_button(
        self,
        connection: Connection,
        game_id: str,
        button_id: str
    ) -> None:
        if game_id not in self.games:
            connection.error('Game id does not exist.')
            return

        game = self.games[game_id]
        game.click_button(connection, button_id)
