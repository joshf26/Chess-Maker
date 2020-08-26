import sys


def user_error(message: str) -> None:
    print(f'\n\n=== ERROR ===\n{message}\n', file=sys.stderr)
    sys.exit(1)
