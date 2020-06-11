import inspect
import os
import sys

import yaml

from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import List, Set, Dict, Type, TypeVar, Union, Optional

from controller import Controller
from decorator import Decorator
from json_serializable import JsonSerializable
from piece import Piece
from user_error import user_error

T = TypeVar('T')
REQUIRED_PACK_FILE_FIELDS = ['name', 'description']


@dataclass
class PackFile:
    name: str
    description: str
    author: Optional[dict]
    source: Optional[str]
    depends_on: Optional[List[str]]


@dataclass
class Pack(JsonSerializable):
    display_name: str
    controllers: List[Type[Controller]]
    pieces: List[Type[Piece]]
    decorators: List[Type[Decorator]]

    def to_json(self) -> Union[dict, list]:
        return {
            'display_name': self.display_name,
            'controllers': {controller.name: {
                'rows': controller.board_size.row,
                'cols': controller.board_size.col,
                'colors': [color.value for color in controller.colors],
                'options': {name: option.to_json() for name, option in controller.options.items()},
            } for controller in self.controllers},
            'pieces': {piece.name: {
                'image': piece.image,
            } for piece in self.pieces},
            'decorators': {decorator.name: {
                'image': decorator.image,
            } for decorator in self.decorators}
        }


def parse_pack_file(path: str) -> PackFile:
    if not os.path.exists(path):
        directory = '/'.join(path.split('/')[:-1])
        user_error(
            f"A new directory ({directory}) was added to the packs directory, but it does not contain a pack.yml file."
            f"\n\nIf you are trying to create a new pack, make sure to include a pack.yml file in the pack's root "
            f"directory.\nIf you are trying to install a pack, make sure you have placed this pack directly in the "
            f"packs directory, and not nested within another directory.",
        )
        sys.exit(1)

    with open(path) as pack_file:
        data = yaml.safe_load(pack_file)

    for required_pack_file_field in REQUIRED_PACK_FILE_FIELDS:
        if required_pack_file_field not in data:
            user_error(f"{path} is missing the {required_pack_file_field} field.")
            sys.exit(1)

    return PackFile(
        data['name'],
        data['description'],
        data.get('author', None),
        data.get('source', None),
        data.get('depends_on', None),
    )


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
        pack_file = parse_pack_file(f'chess_maker/packs/{pack}/pack.yml')
        module = import_module(f'packs.{pack}')
        result[pack] = Pack(
            pack_file.name,
            get_members_of_type(module, Controller),
            get_members_of_type(module, Piece),
            get_members_of_type(module, Decorator),
        )

    return result
