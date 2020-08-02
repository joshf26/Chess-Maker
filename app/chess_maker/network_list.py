from typing import List, Callable, TypeVar, Generic

T = TypeVar('T')


class NetworkList(Generic[T]):

    def __init__(self, exit_handler: Callable[[], None]):
        self.items: List[T] = []
        self.exit_handler = exit_handler

    def __enter__(self):
        return self.items

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_handler()
