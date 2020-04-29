from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

from piece import Piece, load_image
from ply import Ply

if TYPE_CHECKING:
    from game import Game


class Bishop(Piece):
    name = 'Bishop'
    image = load_image('standard', 'images/bishop.svg')

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []
