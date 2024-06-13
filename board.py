class Board:
    """
    Represents the chess board as a collection of 64-bit bitboards.
    Contains methods that, given a specific move, checks through
    bitwise operations what piece of which color is being moved,
    whether that move is legal, and whether a piece was taken.

    Communicates with the ChessVar class, receiving from it player
    moves, handling all the logic of verifying whether the move is legal,
    then executing the move and returning to ChessVar information of the
    result. ChessVar also uses this class to update the game's status by
    checking whether the game's win conditions have been met.
    """
    def __init__(self):
        self._current_turn = "White"
        self._piece_moved_index = None
        self._piece_captured_index = None
        self._piece_names = ["Pawn", "Rook", "Knight", "Bishop", "Queen", "King"]
        self._white_pieces_list = []
        self._black_pieces_list = []
        self._all_white_pieces_bb = 0b0     # bitboard representing all white pieces
        self._all_black_pieces_bb = 0b0     # bitboard representing all black pieces
        self._all_pieces_bb = 0b0           # bitboard representing all pieces
        self.setup_new_board()              # place pieces for a new game

    # ------------------------ Get and Set Methods ------------------------- #
    def get_pieces(self) -> tuple:
        """Returns a tuple containing each color's piece lists."""
        return self._white_pieces_list, self._black_pieces_list

    def get_turn(self) -> str:
        """Returns the color of the current player."""
        return self._current_turn

    def get_piece_moved(self) -> str:
        """
        If _piece_moved_index is not None, returns the name of the type of
        piece represented by the index, and sets piece_moved_index to None.

        :return: Name of a piece type as a string, or None.
        """
        piece_type = self._piece_names[self._piece_moved_index]
        self._piece_moved_index = None
        return piece_type

    def get_piece_captured(self):
        """
        Returns the piece that was captured if a piece was captured
        piece represented by the index, and sets piece_moved_index to None.

        :return: Name of a piece type as a string, or None.
        """
        if self._piece_captured_index is None:
            return None
        piece_type = self._piece_names[self._piece_captured_index]
        self._piece_captured_index = None
        return piece_type

    def set_next_turn(self):
        """Sets the _current_turn to the next player color."""
        if self._current_turn == "White":
            self._current_turn = "Black"
        else:
            self._current_turn = "White"

    # ------------------ Chessboard Representation Methods ----------------- #
    def setup_new_board(self) -> None:
        """
        Sets up a new game by first setting the current player to White, then
        initializing 15 bitboards - one bitboard for all pieces of each color
        (6 each), one for each chess piece type of each color (1 each), and
        one bitboard representing all pieces currently occupying a board tile.

        :return: None.
        """
        self._current_turn = "White"
        # white piece types
        self._white_pieces_list = [
            0b11111111 << 8,        # 0 White Pawn
            0b10000001,             # 1 White Rook
            0b01000010,             # 2 White Knight
            0b00100100,             # 3 White Bishop
            0b00001000,             # 4 White Queen
            0b00010000              # 5 White King
        ]
        self._black_pieces_list = [
            0b11111111 << (8 * 6),  # 0 Black Pawn
            0b10000001 << (8 * 7),  # 1 Black Rook
            0b01000010 << (8 * 7),  # 2 Black Knight
            0b00100100 << (8 * 7),  # 3 Black Bishop
            0b00001000 << (8 * 7),  # 4 Black Queen
            0b00010000 << (8 * 7)   # 5 Black King
        ]
        self._all_white_pieces_bb = 0xffff
        self._all_black_pieces_bb = 0xffff000000000000
        self._all_pieces_bb = 0xffff00000000ffff

    def update_bitboards(self, move_from_bb, move_to_bb) -> None:
        """
        Updates the class's stored bitboards after a successful move.
        :param move_from_bb: Integer representing a 8x8 bitboard.
        :param move_to_bb: Integer representing a 8x8 bitboard.
        :return: None.
        """
        if self._current_turn == "White":
            # update white pieces
            self._white_pieces_list[self._piece_moved_index] &= ~move_from_bb
            self._white_pieces_list[self._piece_moved_index] |= move_to_bb
            self._all_white_pieces_bb = (self._all_white_pieces_bb & ~move_from_bb) | move_to_bb
            opponents_pieces_list = self._black_pieces_list
            all_opponents_pieces_bb = self._all_black_pieces_bb
        else:
            # update black pieces
            self._black_pieces_list[self._piece_moved_index] &= ~move_from_bb
            self._black_pieces_list[self._piece_moved_index] |= move_to_bb
            self._all_black_pieces_bb = (self._all_black_pieces_bb & ~move_from_bb) | move_to_bb
            opponents_pieces_list = self._white_pieces_list
            all_opponents_pieces_bb = self._all_white_pieces_bb

            # update bitboard for all pieces
        self._all_pieces_bb = (self._all_pieces_bb & ~move_from_bb) | move_to_bb

        # test if a piece was captured
        if move_to_bb & all_opponents_pieces_bb:
            for index, piece_type_bb in enumerate(opponents_pieces_list):
                if move_to_bb & piece_type_bb:
                    self._piece_captured_index = index
                    opponents_pieces_list[index] &= ~move_to_bb
                    if self._current_turn == "White":
                        self._all_black_pieces_bb &= ~move_to_bb
                    else:
                        self._all_white_pieces_bb &= ~move_to_bb

    # ----------------------- Move Execution Methods ----------------------- #
    def execute_move(self, move_from: str, move_to: str) -> bool:
        """
        Executes a chess move from one position to another and updates the game state.
        It first translates the board positions from string format to bitboards, then
        validates the move - updating the game's bitboards if the move is legal.
        Also handles captures by storing their type index in '_piece_captured_index'.

        :param move_from: A string of two characters, i.e., "C4".
        :param move_to: A string of two characters, i.e., "A7".
        :return: Boolean - True or False.
        """
        # print(f"{self._current_turn}'s move: "
        #       f"{move_from.upper()} to {move_to.upper()}")

        # ---------- Convert Coordinates to Bitboards --------- #
        # verify that move_from and move_to are not the same
        if move_from.upper() == move_to.upper():
            return False

        # convert 'to' and 'from' locations to bitboards
        move_from_bb = self.convert_to_bitboard(move_from)
        move_to_bb = self.convert_to_bitboard(move_to)
        # verify that locations map to valid locations
        if move_from_bb is None or move_to_bb is None:
            return False

        # ----------------- Find Valid Moves ------------------ #
        # remove the move_from location from all_pieces bitboard
        # (precondition for methods that generate moves)
        self._all_pieces_bb &= ~move_from_bb

        # check that a valid piece is at move_from, then find valid moves
        legal_moves = self.find_valid_moves(move_from_bb)

        # print if move checker found any piece at move_from
        if self._piece_moved_index is not None:
            print(f"{self._current_turn} {self._piece_names[self._piece_moved_index]}"
                  f" found at {move_from.upper()}\n"
                  f"Legal moves: ", end='')
            print(legal_moves)
        else:
            print(f"INVALID MOVE: No piece found at {move_from}\n")
            # return moved piece back to the all_pieces bitboard
            self._all_pieces_bb |= move_from_bb
            return False

        # test if move_to matches any legal moves (there may be 0 legal moves)
        if (move_to_bb & legal_moves) == 0:
            print(f"ILLEGAL MOVE: {move_to.upper()} is invalid\n")
            self._all_pieces_bb |= move_from_bb
            return False

        # ------------------- Execute Move -------------------- #
        # move is legal - perform move by updating bitboards
        # (Also stores any captured piece index in _piece_captured_index)
        self.update_bitboards(move_from_bb, move_to_bb)
        return True

    def find_valid_moves(self, move_from_bb: int):
        """
        Finds all valid moves for a piece located at a specified position.
        First identifies the piece at the location provided, then calls a
        generator method to find all legal moves for that piece based on
        the current game state. Returns an integer representing a bitboard
        containing all valid moves for a specific piece including captures.

        :param move_from_bb: Integer representing a bitboard.
        :return: Integer 64-bit bitboard - all valid moves.
        """
        # initialize piece lists
        if self._current_turn == "White":
            pieces_to_search = self._white_pieces_list
            friendly_pieces_bb = self._all_white_pieces_bb
        else:   # Black's turn
            pieces_to_search = self._black_pieces_list
            friendly_pieces_bb = self._all_black_pieces_bb

        # identify piece using 'bitwise AND' with player's piece bitboards,
        # then return all generated moves that do not end on a friendly piece.
        # 0=pawn, 1=rook, 2=knight, 3=bishop, 4=queen, 5=king

        # Pawn (0)
        if pieces_to_search[0] & move_from_bb:
            self._piece_moved_index = 0
            return self.generate_moves_pawn(move_from_bb) & ~friendly_pieces_bb

        # Rook (1)
        elif pieces_to_search[1] & move_from_bb:
            self._piece_moved_index = 1
            # directions to check (8 = North, -8 = South, 1 = East, -1 = West)
            directions = [8, -8, 1, -1]
            return self.generate_moves(move_from_bb, directions) & ~friendly_pieces_bb

        # Knight (2)
        elif pieces_to_search[2] & move_from_bb:
            self._piece_moved_index = 2
            return self.generate_moves_knight(move_from_bb) & ~friendly_pieces_bb

        # Bishop (3)
        elif pieces_to_search[3] & move_from_bb:
            self._piece_moved_index = 3
            # directions to check (7 = Northwest,  9 = Northeast, -7 = Southeast, -9 = Southwest)
            directions = [7, 9, -7, -9]
            return self.generate_moves(move_from_bb, directions) & ~friendly_pieces_bb

        # Queen (4)
        elif pieces_to_search[4] & move_from_bb:
            self._piece_moved_index = 4
            # directions to check (8=N, -8=S, 1=E, -1=W, 7=NW, 9=NE, -7=SE, -9=SW)
            directions = [8, -8, 1, -1, 7, 9, -7, -9]
            return self.generate_moves(move_from_bb, directions) & ~friendly_pieces_bb

        # King (5)
        elif pieces_to_search[5] & move_from_bb:
            self._piece_moved_index = 5
            # directions to check (8=N, -8=S, 1=E, -1=W, 7=NW, 9=NE, -7=SE, -9=SW)
            directions = [8, -8, 1, -1, 7, 9, -7, -9]
            return self.generate_moves(move_from_bb, directions, move_limit=1) & ~friendly_pieces_bb
        else:
            return 0b0      # No piece of player's color found at location provided.

    # --------------------- Movement Generator Methods --------------------- #
    # - A general movement method and special methods for Knight and Pawn -- #
    def generate_moves_pawn(self, move_from_bb: int):
        """
        Finds all legal moves for a pawn from a provided starting location.
        :param move_from_bb: Integer 64-bit bitboard - single bit for 'move_from' location.
        :return: Integer 64-bit bitboard - all possible moves.
        """
        forward_move_limit = 1

        if self._current_turn == "White":
            # White moves upward
            direction = +1
            # pawn in starting row (rank 2)
            if move_from_bb & 0xff00:
                forward_move_limit = 2
        else:
            # Black moves downward
            direction = -1
            # pawn in starting row (rank 7)
            if move_from_bb & 0xff000000000000:
                forward_move_limit = 2

        # check vertical moves (8 = North, -8 = South)
        valid_moves_bb = self.generate_moves(move_from_bb, [8 * direction], forward_move_limit)
        # remove any moves that end on another piece (vertical moves cannot capture)
        valid_moves_bb &= ~self._all_pieces_bb
        # get diagonal moves (7 = NW, 9 = NE, -7 = SE, -9 = SW)
        diagonal_moves = self._all_pieces_bb
        # only keep diagonal moves that end on another piece
        diagonal_moves &= self.generate_moves(move_from_bb, [7 * direction, 9 * direction], 1)
        valid_moves_bb |= diagonal_moves
        return valid_moves_bb

    @staticmethod
    def generate_moves_knight(move_from_bb: int) -> int:
        """
        Finds all legal moves for a knight from a provided starting location.
        :param move_from_bb: Integer 64-bit bitboard - single bit for 'move_from' location.
        :return: Integer 64-bit bitboard - all possible moves.
        """
        # Create border boundary based on location's board quadrant,
        # storing the directions to shift the piece location bitboard.
        # (Q1 = NW border, Q2 = N&E border, Q3 = SW border, Q4 = SE border)

        boundary_bb = 0x0
        knight_bb = move_from_bb
        left_bit_shifts = right_bit_shifts = 0

        # North half (Q1 + Q2)
        if knight_bb & 0xffffffff00000000:
            boundary_bb |= -0xffff000000000000      # add North boundary
            right_bit_shifts += 8 * 2               # shift knight's bb South
        # South half (Q3 + Q4)
        else:
            boundary_bb |= 0xffff                   # add South boundary
            left_bit_shifts += 8 * 2                # shift knight's bb North

        # West half (Q1 + Q3)
        if knight_bb & 0xf0f0f0f0f0f0f0f:
            boundary_bb |= 0x303030303030303        # add West boundary
            left_bit_shifts += 2                    # shift knight's bb East
        # East half (Q2 + Q4)
        else:
            boundary_bb |= 0xc0c0c0c0c0c0c0c0       # add East boundary
            right_bit_shifts += 2                   # shift knight's bb West

        # shift piece's bitboard location so edge-most bits represent beyond the board
        knight_bb = (knight_bb >> right_bit_shifts) << left_bit_shifts

        moves_bb = 0b0
        # find all possible movements relative to knights position by finding all
        # combinations of left and right shifts, distances (1, 2), and directions (8, 1)
        for leg_one in [1, 2]:
            leg_two = 3 - leg_one  # switches between 2 and 1
            for multiplier in [1, 8]:
                multiplier2 = 9 - multiplier  # switches between 8 and 1
                # Apply the first set of shifts and accumulate
                moves_bb |= (knight_bb >> (leg_one * multiplier)) >> (leg_two * multiplier2)
                moves_bb |= (knight_bb >> (leg_one * multiplier)) << (leg_two * multiplier2)
                moves_bb |= (knight_bb << (leg_one * multiplier)) >> (leg_two * multiplier2)
                moves_bb |= (knight_bb << (leg_one * multiplier)) << (leg_two * multiplier2)

        # crop out-of-bounds moves
        moves_bb &= ~boundary_bb
        # shift moves_bb to original location (no out-of-bounds bits shown/represented)
        return (moves_bb << right_bit_shifts) >> left_bit_shifts

    def generate_moves(self, origin_bb, directions: list, move_limit=None) -> int:
        """
        Tests and accumulates all possible moves from a given origin in
        specified directions up to a move limit. This method calculates
        possible moves in linear directions by recursively shifting bits.
        It calls recc_left_shift to generate all moves between East to
        Northwest, and recc_right_shift to handle all moves between West
        to Southeast. It also handles Board boundaries and piece collisions.

        << = East-Northwest (increment):
            <<1 = East, <<8 = North, <<7 = Northwest, <<9 = Northeast
        >> = West-Southeast (decrement):
            >>1 = West, >>8 = South, >>7 = Southeast, >>9 = Southwest

        :param origin_bb: Integer 64-bit bitboard - a single set bit indicating origin.
        :param directions: List of integers representing the directions to test for moves.
        :param move_limit: Optional parameter to limit move search (ex: 1 for kings and pawns).
        :return: Integer 64-bit bitboard representing all possible moves.
        """
        moves_result_bb = 0b0

        for direction in directions:
            if direction > 0:
                moves_result_bb |= self.recc_left_shift(origin_bb, direction, move_limit)
            elif direction < 0:
                moves_result_bb |= self.recc_right_shift(origin_bb, abs(direction), move_limit)

        return moves_result_bb

    # --------------------- Recursive Movement Checkers -------------------- #

    def recc_left_shift(self, location_bb, direction, move_limit_count) -> int:
        """
        Recursive function which returns a bitboard of all possible moves in
        a direction from East to Northwest up until and including the nearest
        collision with a piece on the board. Combined with recc_right_shift,
        all linear movements can be tested.

        Uses bit shift left (<<) with the following values:
        1 = East,  8 = North,  7 = Northwest,  9 = Northeast

        :param location_bb: Integer bitboard - a single set bit.
        :param direction: Integer (1, 7, 8, or 9)
        :param move_limit_count:
        :return: Integer 64-bit bitboard - possible moves.
        """
        # manage count if a move limit is set
        if move_limit_count is not None:
            if move_limit_count <= 0:
                return 0b0
            move_limit_count -= 1

        # conditions for N (8)
        if direction == 8:
            # check if at boundary (rank 8), or collision with piece
            if location_bb & 0xff00000000000000 or location_bb & self._all_pieces_bb:
                return 0b0
        # conditions for E (1)
        elif direction == 1:
            # check if at boundary (file 'H'), or collision with piece
            if location_bb & 0x8080808080808080 or location_bb & self._all_pieces_bb:
                return 0b0
        # conditions for NW (7)
        elif direction == 7:
            # check if at boundary (row 8 + rank 'A'), or collision with piece
            if location_bb & 0xff01010101010101 or location_bb & self._all_pieces_bb:
                return 0b0
        # conditions for NE (9)
        elif direction == 9:
            # check if at boundary (row 8 + rank H), or collision with piece
            if location_bb & 0xff80808080808080 or location_bb & self._all_pieces_bb:
                return 0b0

        destination_bb = (location_bb << direction)         # shift left to find next location
        return destination_bb | self.recc_left_shift(destination_bb, direction, move_limit_count)

    def recc_right_shift(self, location_bb, direction, move_limit_count) -> int:
        """
        Recursive function which returns a bitboard of all possible moves in
        a direction from East to Northwest up until and including the nearest
        collision with a piece on the board. Combined with recc_left_shift,
        all linear movements can be tested.

        Uses bit shift right (>>) with the following values:
        1 = West, 8 = South, 7 = Southeast, 9 = Southwest

        :param location_bb: Integer 64-bit bitboard - a single set bit.
        :param direction: Integer (1, 7, 8, or 9)
        :param move_limit_count:
        :return: Integer 64-bit bitboard - possible moves.
        """
        # manage count if a move limit is set
        if move_limit_count is not None:
            if move_limit_count <= 0:
                return 0b0
            move_limit_count -= 1

        # set conditions for S (8)
        if direction == 8:
            # check if at boundary (rank 1), or collision with piece
            if location_bb & 0xff or location_bb & self._all_pieces_bb:
                return 0b0
        # set conditions for W (1)
        elif direction == 1:
            # check if at boundary (file 'A'), or collision with piece
            if location_bb & 0x101010101010101 or location_bb & self._all_pieces_bb:
                return 0b0
        # set conditions for SE (7)
        elif direction == 7:
            # check if at boundary (rank 1 + file 'H'), or collision with piece
            if location_bb & 0x80808080808080ff or location_bb & self._all_pieces_bb:
                return 0b0
        # set conditions for SW (9)
        elif direction == 9:
            # check if at boundary (rank 1 + file 'A'), or collision with piece
            if location_bb & 0x1010101010101ff or location_bb & self._all_pieces_bb:
                return 0b0

        destination_bb = (location_bb >> direction)     # shift right to find next location
        return destination_bb | self.recc_right_shift(destination_bb, direction, move_limit_count)

    # -------------------------- Utility Methods --------------------------- #
    @staticmethod
    def convert_to_bitboard(location):
        """
        Given a rank and file coordinate, first checks if it is a valid
        location within the rank and file coordinate system, then converts
        it to a bitboard and returns it. Otherwise, returns None.

        :param location: two-char string representing file and rank.
        :return: Integer 64-bit bitboard or None.
        """
        if not isinstance(location, str):
            return None
        if len(location) != 2:
            return None

        # file and rank to ints
        file = ord(location[0].upper()) - ord('A')
        rank = int(location[1]) - 1

        if file < 0 or file > 7:
            return None
        if rank < 0 or rank > 7:
            return None

        # return bitboard location by shifting from 0x1 (A1)
        return 0b1 << (8*rank + file)
