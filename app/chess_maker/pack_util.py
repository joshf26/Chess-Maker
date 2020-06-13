from typing import Tuple, Dict, Union

from PIL import Image

from decorator import Decorator
from vector2 import Vector2


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
