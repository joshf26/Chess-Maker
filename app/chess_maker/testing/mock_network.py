from typing import Callable

from ..network import Network


class MockNetwork(Network):

    def command(self, game_id: str = None):
        def inner(function: Callable):
            pass

        return inner
