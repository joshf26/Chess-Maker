import inspect
import os
from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import List, Set, Dict, Type, TypeVar

from controller import Controller
from piece import Piece

T = TypeVar('T')


@dataclass
class Pack:
    controllers: List[Type[Controller]]
    pieces: List[Type[Piece]]


def available_packs() -> Set[str]:
    return {
        filename
        for filename in os.listdir('chess_maker/packs')
        if filename != '__pycache__' and filename != '__init__.py'
    }


def get_members_of_type(module: ModuleType, class_type: Type[T]) -> List[Type[T]]:
    return [cls[1] for cls in inspect.getmembers(module, lambda cls: inspect.isclass(cls) and class_type in cls.__bases__)]
        

def load_packs() -> Dict[str, Pack]:
    result: Dict[str, Pack] = {}

    for pack in available_packs():
        module = import_module(f'packs.{pack}')
        result[pack] = Pack(
            get_members_of_type(module, Controller),
            get_members_of_type(module, Piece),
        )

    return result
