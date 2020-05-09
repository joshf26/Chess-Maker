from __future__ import annotations
from typing import List, TYPE_CHECKING

from board import InfoText

if TYPE_CHECKING:
    from board import InfoElement
    from game import Game


def get_color_info_texts(game: Game, trailing_space=False) -> List[InfoElement]:
    return [InfoText(
        f'<strong style="color: {color.name.lower()}">{color.name.title()}</strong>: '
        f'{connection.nickname if (connection := game.players.get_connection(color)) is not None else "<em>Waiting...</em>"}'
    ) for color in game.board.colors] + ([InfoText('<br>')] if trailing_space else [])
