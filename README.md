# Chess Config

An experiment to determine the requirements for encoding the rules of chess into a single configuration file.

This is currently a WIP.

### Motivation 
A pawn in chess has behavior that is relatively easy to write in code.

```
move_valid(board, first_turn, pawn, x,  y):
    if first_turn and
       x == pawn.x and 
       y == pawn.y + 2 and 
       board[x][y - 1] == empty and
       board[x][y] == empty: Pawn Can Move

    else if x == pawn.x and 
       y == pawn.y + 1 and 
       board[x][y] == empty: Pawn Can Move

    else if x == pawn.x -/+ 1 and
       y == pawn.y + 1 and
       board[x][y] != empty: Pawn Can Move (and capture)

    else Pawn Can't Move
```

But how would we write this in a configuration file that can be generalized for all chess pieces?

How about this?
```yaml
pawn:
  move_forward_spaces: 1
  move_two_spaces_on_first_turn: yes
  attack_forward_diagonally: yes
  becomes_queen_at_end: yes 
```

Well, that's a lot of rules that would have to be set up in code.
Also, these rules are all specific to pawns and can not be reused for other pieces.

My goal for this project is to encode the rules of chess into a config file that requires as little code as possible to interpret.

Once this is complete, this project can become an engine for creating custom chess games where new pieces can be defined by simply updating a config file. 
