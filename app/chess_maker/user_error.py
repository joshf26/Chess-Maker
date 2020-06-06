import sys


def user_error(message: str) -> None:
    print(f'\n\n=== ERROR ===\n{message}', file=sys.stderr)
    sys.exit(1)
