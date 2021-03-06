from __future__ import annotations

from typing import TYPE_CHECKING, Union

from .controller import Controller
from .decorator import Decorator

if TYPE_CHECKING:
    from piece import Piece


def get_pack(obj: Union[Piece, Controller, Decorator]) -> str:
    return obj.__module__.split('.')[1]
