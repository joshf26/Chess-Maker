from boards.standard import Standard8x8
from game import Game


def main():
    game = Game(Standard8x8())

    print(game.board.ascii)


if __name__ == '__main__':
    main()
