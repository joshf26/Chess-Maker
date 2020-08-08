from typing import Dict

from color import Color
from game import Game, ChatMessage
from game_subscribers import GameSubscribers
from network import Connection, Network
from pack import Pack
from vector2 import Vector2


class Server:

    def __init__(self, packs: Dict[str, Pack]):
        self.packs = packs

        self.games: Dict[str, Game] = {}
        self.subscribers = GameSubscribers()
        self.network = Network(self.on_connect, self.on_disconnect)
        self._register_commands()

    def _register_commands(self) -> None:
        self.network.register_command('create_game', self.on_create_game)
        self.network.register_command('delete_game', self.on_delete_game)
        self.network.register_command('show_game', self.on_show_game)
        self.network.register_command('join_game', self.on_join_game)
        self.network.register_command('leave_game', self.on_leave_game)
        self.network.register_command('plies', self.on_plies)
        self.network.register_command('inventory_plies', self.on_inventory_plies)
        self.network.register_command('submit_ply', self.on_submit_ply)
        self.network.register_command('click_button', self.on_click_button)
        self.network.register_command('send_chat_message', self.on_send_chat_message)

    def start(self, port: int) -> None:
        self.network.serve(port)

    def on_connect(self, connection: Connection) -> None:
        self.network.all_update_players()
        connection.set_player()
        connection.update_pack_data(self.packs)
        connection.update_game_metadata(self.games)

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
            self.network.all_update_game_metadata(self.games)

        self.network.all_update_players()

    def on_create_game(
        self,
        connection: Connection,
        name: str,
        controller_pack_id: str,
        controller_id: str,
        options: dict,
    ) -> None:
        if controller_pack_id not in self.packs:
            connection.show_error('Package does not exist.')
            return

        controller_class = next(filter(
            lambda b: b.name == controller_id,
            self.packs[controller_pack_id].controllers,
        ), None)

        if controller_class is None:
            connection.show_error('Controller does not exist.')
            return

        if options.keys() != controller_class.options.keys():  # TODO: Improve error reporting and add type checking.
            connection.show_error('Options not supplied successfully.')
            return

        game = Game(name, connection, controller_class, options, self.network, self.subscribers)
        self.games[game.id] = game

        self.network.all_update_game_metadata(self.games)
        connection.focus_game(game)

    def on_delete_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.show_error('Game does not exist.')
            return

        if self.games[game_id].owner.display_name != connection.display_name:
            connection.show_error('Only the owner of this game can delete it.')
            return

        self.subscribers.remove_game(self.games[game_id])
        self.games[game_id].shutdown()
        del self.games[game_id]
        self.network.all_update_game_metadata(self.games)

    def on_show_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.show_error('Game does not exist.')
            return

        game = self.games[game_id]
        self.subscribers.set(game, connection)
        connection.update_game_data(game)

    def on_join_game(self, connection: Connection, game_id: str, color: int) -> None:
        if game_id not in self.games:
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection in game.players:
            connection.show_error('Player is already in this game.')
            return

        color_object = next(filter(lambda x: x.value == color, Color.__iter__()), None)

        if color_object is None:
            connection.show_error('Color does not exist.')
            return

        if color_object in game.players:
            connection.show_error('That color is already taken in this game.')
            return

        game.add_player(connection, color_object)

        self.network.all_update_game_metadata(self.games)
        game.send_update_to_subscribers()

    def on_leave_game(self, connection: Connection, game_id: str) -> None:
        if game_id not in self.games:
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            connection.show_error('Player is not in this game.')
            return

        if connection in game.players:
            game.players.remove_connection(connection)

        self.network.all_update_game_metadata(self.games)
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
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]

        if connection not in game.players:
            connection.show_error('Player is not in this game.')
            return

        from_pos = Vector2(from_row, from_col)
        to_pos = Vector2(to_row, to_col)

        plies = list(game.get_plies(connection, from_pos, to_pos))
        game.apply_or_offer_choices(from_pos, to_pos, plies, connection)

    def on_inventory_plies(
        self,
        connection: Connection,
        game_id: str,
        inventory_item_id: str,
        to_row: int,
        to_col: int,
    ) -> None:
        if game_id not in self.games:
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]
        inventory = game.inventories[game.players.get_color(connection)].items
        inventory_item = next(filter(lambda item: item.id == inventory_item_id, inventory), None)

        if not inventory_item:
            connection.show_error('You do not have that item in your inventory.')
            return

        if connection not in game.players:
            connection.show_error('Player is not in this game.')
            return

        to_pos = Vector2(to_row, to_col)
        color = Color(inventory_item.piece.color)
        inventory_plies = list(game.controller.get_inventory_plies(color, inventory_item.piece, to_pos))

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
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]
        color = game.players.get_color(connection)
        plies = list(game.get_plies(connection, Vector2(from_row, from_col), Vector2(to_row, to_col)))
        dict_plies = [ply_data.to_json() for ply_data in plies]

        if ply not in dict_plies:
            connection.show_error('Ply not available.')
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
            connection.show_error('Game id does not exist.')
            return

        game = self.games[game_id]
        game.click_button(connection, button_id)

    def on_send_chat_message(self, connection: Connection, text: str, game_id: str) -> None:
        if game_id == 'server':
            for other_connection in self.network.connections:
                other_connection.receive_server_chat_message(text, connection)
        else:
            if game_id not in self.games:
                connection.show_error('Game id does not exist.')
                return

            game = self.games[game_id]
            game.chat_messages.append(ChatMessage(connection, text))
            for other_connection in self.subscribers.get_connections(game):
                other_connection.receive_game_chat_message(game, connection, text)
