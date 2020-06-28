from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Dict, Union

from PIL import Image

from controller import Controller
from decorator import Decorator
from vector2 import Vector2

if TYPE_CHECKING:
    from piece import Piece


def get_pack(obj: Union[Piece, Controller, Decorator]) -> str:
    return obj.__module__.split('.')[1]


def load_image(pack_path: str, image_path: str) -> str:
    with open(f'chess_maker/packs/{pack_path}/{image_path}') as file:
        return file.read()


def decorators_from_image(
    pack_path: str,
    image_path: str,
    color_mapping: Union[Dict[int, Decorator], Dict[tuple, Decorator]],
) -> Tuple[Vector2, Dict[Vector2, Decorator]]:
    result: Dict[Vector2, Decorator] = {}
    image = Image.open(f'chess_maker/packs/{pack_path}/{image_path}')
    data = image.getdata()

    for row in image.height:
        for col in image.width:
            pixel = data[row * image.width + col]
            if pixel in color_mapping:
                result[Vector2(row, col)] = color_mapping[pixel]
            else:
                print(f'WARNING: No mapping for color {pixel} found. Ignoring pixel at row {row}, col {col}.')

    return Vector2(image.height, image.width), result
