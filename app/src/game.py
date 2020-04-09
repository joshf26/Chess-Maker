from board import Board
from network import Network, ReplyCallable, ErrorCallable


class Game:

    def __init__(self, board: Board, network: Network):
        self.board = board
        self.network = network

    def join_as_color(self, reply: ReplyCallable, error: ErrorCallable, parameters: dict):
        if 'color' not in parameters:
            error('Color Not Specified')
            return
