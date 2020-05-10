from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from piece import Piece, load_image

if TYPE_CHECKING:
    from ply import Ply
    from game import Game


class Wall(Piece):
    name = 'Wall'
    image = load_image('standard', 'images/wall.svg')

    def ply_types(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], game: Game) -> List[Tuple[str, Ply]]:
        return []
