from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from piece import Piece, load_image

if TYPE_CHECKING:
    from ply import Ply
    from game import Game
    from board import Vector2


class Wall(Piece):
    name = 'Wall'
    image = load_image('standard', 'images/wall.svg')

    def ply_types(self, from_pos: Vector2, to_pos: Vector2, game: Game) -> List[Tuple[str, Ply]]:
        return []
