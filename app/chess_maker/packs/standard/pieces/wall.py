from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from color import Color
from piece import Piece, load_image, Direction

if TYPE_CHECKING:
    from ply import Ply
    from game import Game


class Wall(Piece):
    name = 'Wall'
    image = load_image('standard', 'images/wall.svg')

    def __init__(self):
        # The direction of a wall does not matter, so just construct it with an arbitrary direction.
        super().__init__(Color.NONE, Direction.NORTH)

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []
