from __future__ import annotations

from typing import Dict, Set, Optional, TYPE_CHECKING

from network import Connection

if TYPE_CHECKING:
    from game import Game


class GameSubscribers:

    def __init__(self):
        self.connection_to_game: Dict[Connection, Game] = {}
        self.game_to_connections: Dict[Game, Set[Connection]] = {}

    def set(self, game: Game, connection: Connection) -> None:
        # Remove the old subscription.
        if connection in self.connection_to_game:
            previous_game = self.connection_to_game[connection]
            self.game_to_connections[previous_game].remove(connection)

        # Add the new subscription.
        if game in self.game_to_connections:
            self.game_to_connections[game].add(connection)
        else:
            self.game_to_connections[game] = {connection}

    def get_connections(self, game: Game) -> Set[Connection]:
        if game in self.game_to_connections:
            return self.game_to_connections[game]

        return set()

    def get_game(self, connection: Connection) -> Optional[Game]:
        return self.connection_to_game.get(connection, None)
