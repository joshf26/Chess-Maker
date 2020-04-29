from typing import TYPE_CHECKING, Tuple, List

from piece import Piece
from ply import Ply

if TYPE_CHECKING:
    from game import Game


class Queen(Piece):
    name = 'Queen'
    image = 'images/queen.svg'

    # TODO

    def ply_types(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        game: Game,
    ) -> List[Ply]:
        return []
