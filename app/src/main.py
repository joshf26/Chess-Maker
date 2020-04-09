from network import Network, ReplyCallable, ErrorCallable

PORT = 8000


def main():
    network = Network()
    games = {}

    @network.command
    async def create_game(reply: ReplyCallable, error: ErrorCallable, player1: str, player2: str):
        await reply({
            'message': 'Success!',
        })

    network.serve(8000)


if __name__ == '__main__':
    main()
