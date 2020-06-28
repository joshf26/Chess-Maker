import os

from pack import load_packs
from server import Server


def splash() -> None:
    print(r"                                                 ")
    print(r"  / __| |_  ___ ______ |  \/  |__ _| |_____ _ _  ")
    print(r" | (__| ' \/ -_|_-<_-< | |\/| / _` | / / -_) '_| ")
    print(r"  \___|_||_\___/__/__/ |_|  |_\__,_|_\_\___|_|   ")
    print(r"                                                 ")


if __name__ == '__main__':
    splash()
    server = Server(load_packs())
    server.start(int(os.environ['PORT']))
