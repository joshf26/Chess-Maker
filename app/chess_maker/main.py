import os

from pack import load_packs
from server import Server

if __name__ == '__main__':
    server = Server(load_packs())
    server.start(int(os.environ['PORT']))
