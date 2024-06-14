# ChessVariant
*A simple, bitboard-based chess variant built blindly from scratch.*

In the spirit of learning through blunder, none of the binary chess techniques here were borrowed from or inspired by any other source, aside from the storing of piece information in separate bitboards. A possibly embarassing and novel approach to moving a knight can be found detailed below.

In this limited version of chess, the board state and all move calculations are carried out through the use of bitboards and bitwise operations. The game itself consists of all the legal moves of chess except for en-passant and castling. There is no check or check-mate, and the first player to capture all of the opponents pieces of one type wins.

`python chessVar.py` to play

## :diamonds: Interface:

![interface](https://github.com/flwrr/ChessVariant/assets/141792497/3a86d58c-3d19-4130-ace7-c81a703eef68)

## :diamonds: Bitwise Movement

   The left bitboard below represents all white pawns. (1 = pawn)
   if the bottom left bit of this 8x8 bitboard is the 0th bit,
   and the top right bit of the bitboard represents the 63rd bit,
   then the bitboard is also equal to the binary number:
   `0b1111111100000000`, and the decimal number: `65280`.

   The bitboard on the right is the result of shifting the bits
   of the first bitboard to the left by 8 `65280 << 8`. This same
   method will be used while determining all legal rules of a few
   types of chess pieces, including the rook, king, queen, and pawn.
```
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          1  1  1  1  1  1  1  1
      1  1  1  1  1  1  1  1          0  0  0  0  0  0  0  0
      0  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
```
   This 8x8 bitboard calculator was very useful:
   https://gekomad.github.io/Cinnamon/BitboardCalculator/

### Python's bitwise operators

1. **LEFT SHIFT** `x << y`<br>
   Shifts bits to the left by *y* places. All new bits on the right are 0.<br>
   Equivalent to `x * 2**y`. This is used to move pieces:
   * left `x << 1`
   * up `x << 8`
   * diagonally up-right `x << 7`
   * diagonally up-left `x << 9`


2. **RIGHT SHIFT** `x >> y`<br>
   Shifts bits to the right by *y* places. All new bits on the left are 0.<br>
   Equivalent to `x // 2**y`. This is used to move pieces:
   * right `x >> 1`
   * down `x >> 8`
   * diagonally down-left `x >> 7`
   * diagonally down-right `x >> 9`
     

3.  **BITWISE 'AND'** `x & y`<br>
   Performs an 'and' of all of x and y's bits. ex. `0011b & 1111b = 0011b`.<br>
   Used to find moves that collide with other pieces such as pawn attacks.


4.  **BITWISE 'OR'** `x | y`<br>
   Performs an 'or' of all of x and y's bits. ex. `0011b | 1000b = 1011b`.<br>
   Used to combine different bitboards or adding moves with special conditions such as pawn double-jump.


5.  **BITWISE 'NOT'** `~ x`<br>
   Performs a 'not' of x, or returns the compliment of x by flipping all of x's bits.<br>
   Equivalent to: `-x -1 (inverse of two's compliment)`
   
7.  **bitwise 'xor'** `x ^ y`<br>
   Performs a 'xor' of all of x, y's bits. ex. `0111b ^ 1110b = 1001b`<br>
   Used to remove or add bits to bitboards in the case of movement or captures.

## :diamonds: Example: Moving A Rook

   After determining that the move_from location coincides with a
   piece belonging to the player whose turn it is to move, and finding
   what type of chess piece that is, the Board class will generate a
   bitboard representing all legal moves for that piece. These are the
   general steps for that process for a rook:

### A. Direction
   Given these two initial bitboards representing possibled vertical or horizontal moves, we can determine whether the
   intended 'move_to' location would be legal on a blank board, then determine in which direction the move would be:
```
   0x8080808080808080              0xff
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          0  0  0  0  0  0  0  0
   1  0  0  0  0  0  0  0          1  1  1  1  1  1  1  1
```
   An example move_from of "C4" converted to a tuple of indexes
   representing the file and rank of the board would be (2, 3).
   This tuple can then be used to generate the possible
   horizontal and vertical moves available to a rook given
   a blank board:
```
   0x0x8080808080808080 >> 2       0xff << 8*3
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          1  1  1  1  1  1  1  1
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
   0  0  1  0  0  0  0  0          0  0  0  0  0  0  0  0
```
   An 'and' operation with the bitboard representing the move_to and
   either of these bitboards would mean the rook is capable of moving
   in that vector. To find direction, we see whether the bitboard
   that resulted from the 'and' operation (consisting of a single bit)
   is less than or greater than the bitboard representing the move_from.

   If less than, and the match was with the bitboard representing
   horizontal moves, then we know the move was to the right. If
   greater than, and the match was with the bitboard representing
   vertical moves, then the move was up.

### B. Collision
   After determining direction, we need to check whether that piece,
   before reaching its destination, would collide with any piece along
   the way. To do this, we just bit-shift the rook in the direction
   of the move_to (<<1 for left, >>1 for right, <<8 for up, >>8 for down),
   then check whether the new position matches ('and') the move_to or
   any piece on the board (collision) until it matches it the move-to.
   any match prior to reaching the destination would be illegal.

   Once the destination is reached, then we can check if the move_to
   coincides with any of the player's pieces (illegal), or any of the
   opposing player's pieces (signifies a capture).

   pseudocode for moving left:
```
   capture = False
   illegal = False

   while position != destination and position != any_piece:
      move position 1 to the left
      if position == any_piece:
          illegal = True
          end
   if position == destination:
          if position == my_piece:
              illegal = True
              end
          if position == enemy_piece:
              capture = True
              end
```
