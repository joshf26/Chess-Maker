import inspect
import os

from importlib import import_module
from types import ModuleType
from typing import List, Tuple, Set, Dict, Type

from board import Board
from piece import Piece


def list_available_packs() -> Set[str]:
    return {
        filename
        for filename in os.listdir('chess_maker/packs')
        if filename != '__pycache__' and filename != '__init__.py'
    }


def get_members_of_type(module: ModuleType, class_type: Type):
    return inspect.getmembers(module, lambda cls: inspect.isclass(cls) and class_type in cls.__bases__)
        

def load_packs() -> Dict[str, Tuple[List[Type[Board]], List[Type[Piece]]]]:
    result: Dict[str, Tuple[List[Type[Board]], List[Type[Piece]]]] = {}
    packs = list_available_packs()

    for pack in packs:
        module = import_module(f'packs.{pack}')
        result[pack] = ([], [])

        board_classes = get_members_of_type(module, Board)
        piece_classes = get_members_of_type(module, Piece)

        for name, cls in board_classes:
            result[pack][0].append(cls)
            print(f'Registering board: {name}')

        for name, cls in piece_classes:
            result[pack][1].append(cls)
            print(f'Registering piece: {name}')

    return result
