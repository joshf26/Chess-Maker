# Chess Config

An experiment to determine the requirements for encoding the rules of chess into a single configuration file.

This is currently a WIP.

### Motivation 
Pawns in chess are by far the most complicated piece.
Here is how a pawn might be implemented in code:

```
move_valid(game, board, pawn, x, y):
    # Advance two space on first turn.
    if game.first_turn and
       x = pawn.x and 
       y = pawn.y + 2 and 
       board[x][y - 1] = empty and
       board[x][y] = empty: Pawn Can Move

    # Advance one space.
    else if x = pawn.x and 
            y = pawn.y + 1 and 
            board[x][y] = empty: Pawn Can Move

    # Capture diagonally.
    else if x = pawn.x -/+ 1 and
            y = pawn.y + 1 and
            board[x][y] != empty: Pawn Can Move (and capture)

    # En passant.
    else if game.last_move.piece = Pawn and
            |game.last_move.end.y - game.last_move.start.y| = 2 and 
            game.last_move.end.y = pawn.y and
            y = pawn.y + 1 and (
                (game.last_move.end.x = pawn.x - 1 and
                 x = pawn.x - 1) or
                (game.last_move.end.x = pawn.x + 1 and
                 x = pawn.x + 1)
            ): Pawn Can Move (and capture)

    else Pawn Can't Move
```

But how would we write this in a configuration file that can be generalized for all chess pieces?

How about this?
```yaml
pawn:
  move_forward_spaces: 1
  move_two_spaces_on_first_turn: yes
  attack_forward_left_spaces: 1
  attack_forward_right_spaces: 1
  becomes_queen_at_end: yes
  en_passant: yes
```

Well, that's a lot of rules that would have to be set up in code.
Also, these rules are all specific to pawns and can not be reused for other pieces.

My goal for this project is to encode the rules of chess into a config file that requires as little code as possible to interpret.

Once this is complete, this project can become an engine for creating custom chess games where new pieces can be defined by simply updating a config file. 
