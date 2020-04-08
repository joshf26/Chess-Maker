from network import Network, ReplyCallable

PORT = 8000


async def test_command(reply: ReplyCallable, parameters: dict):
    await reply({
        'Hello': 'World',
    })


if __name__ == '__main__':
    network = Network()
    network.commands['test'] = test_command

    network.serve(8000)
