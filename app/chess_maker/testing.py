from typing import TYPE_CHECKING
from unittest.mock import Mock

from game import Game

if TYPE_CHECKING:
    from board import Board


def make_test_game(board: Board):
    return Game('Test Game', Mock(), board, Mock())
