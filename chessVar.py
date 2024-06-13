import board as b


class ChessVar:
    """
    Represents a variant of a chess game. initialization of the game,
    tracking game state, player moves, and displaying an updated
    representation of the board each turn. This class communicates
    with the Board class by passing to it player moves to check what
    piece is being moved, whether the given move is legal, and if so,
    executing that move and updating the representation of the board.
    """
    def __init__(self):
        self._game_state = 'UNFINISHED'
        self._previous_move = None
        self._board = b.Board()
        self._board_display = []
        self.setup_display()
        self.show_display()

    # --------------------------- Game Methods ----------------------------- #
    def get_game_state(self):
        """
        Gets bitboards representing piece locations from the Board object
        following a successful move to update the game's current status.

        :return: 'UNFINISHED', 'WHITE_WON', or 'BLACK_WON'
        """
        white_pieces, black_pieces = self._board.get_pieces()

        # check if black has lost all pieces of a type
        for piece_type in white_pieces:
            if piece_type == 0:
                return "BLACK_WON"

        # check if black has lost all pieces of a type
        for piece_type in black_pieces:
            if piece_type == 0:
                return "WHITE_WON"
        return "UNFINISHED"

    def get_player_turn(self) -> str:
        return self._board.get_turn()

    def make_move(self, move_from: str, move_to: str) -> bool:
        """
        Handles move inputs from players and communicates with the class's
        'board' object to verify, execute, and display the result of that
        move and a visual representation of the resulting chess board.

        Takes two input strings that represent the square moved from and the
        square moved to. Passes to the Board object the move instruction
        received from the player, and receives back whether the move was
        successful. If successful, it will update and display its own visual
        representation of the game to reflect the successful move. Tt will
        then check if  the game's win condition has been met and update the
        board's '_previous_move' info before updating the board class's
        '_current_turn' to the next color.

        :param move_from: File and rank coordinates as a two-char string.
        :param move_to: File and rank coordinates as a two-char string.
        :return: Bool indicating whether move was legal.
        """
        if self.get_game_state() != "UNFINISHED":
            print("Game over. No moves allowed.")
            return False

        if not self._board.execute_move(move_from, move_to):
            return False

        self._game_state = self.get_game_state()
        self.update_display(move_from, move_to)
        self._board.set_next_turn()
        self.show_display()

        return True

    # -------------------------- Display Methods --------------------------- #
    def setup_display(self):
        """
        Sets the initial state of the chess board as a 2d-array.
        Each black piece is represented by an uppercase letter,
        each white piece is represented by a lowercase letter,
        and each empty space is represented by a period, '.'

        :return: None.
        """
        board = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
                 ['P' for _ in range(8)]]
        for _ in range(4):
            board.append(['.' for _ in range(8)])

        board.append(['p' for _ in range(8)])
        board.append([piece.lower() for piece in board[0]])
        self._board_display = board

    def update_display(self, move_from, move_to):
        """
        Updates the display board by moving a chess piece using the arguments provided.
        Must only be used after a successful move to accurately match _board's bitboards.

        :param move_from: File and rank coordinates as a two-char string.
        :param move_to: File and rank coordinates as a two-char string.
        :return: None.
        """
        # convert rank-and-file coordinates to indexes
        from_file = ord(move_from[0].upper()) - ord('A')
        from_rank = int(move_from[1]) - 1
        to_file = ord(move_to[0].upper()) - ord('A')
        to_rank = int(move_to[1]) - 1

        # get piece and remove it from original location
        piece = self._board_display[from_rank][from_file]
        self._board_display[from_rank][from_file] = '.'

        # place piece at new location
        self._board_display[to_rank][to_file] = piece

        # update _previous_move tuple using the format:
        # (player, piece_moved, moved_from, moved_to, piece_captured)
        # ex: ("Black", "Rook", "A1", "B2", None)
        turn = self._board.get_turn()
        moved = self._board.get_piece_moved()
        captured = self._board.get_piece_captured()
        self._previous_move = (turn, moved, move_from, move_to, captured)

    def show_display(self, files_and_columns=True):
        """
        Displays the current state of the board, then prints below it the
        previous move that was made. Includes an optional boolean parameter
        that, by default, that labels the ranks and files of the chessboard.

        :param files_and_columns: 'False' will hide rank and files.
        :return: None.
        """
        print_ranks_and_files = True
        border_top = '`'
        border_bottom = '.'
        border_h_end_top = '.'
        border_h_end_bot = '`'
        border_sides = '|'
        h_spacing = 2

        # print files (A - H)
        print("\n ", end="  " * h_spacing)
        columns = 'ABCDEFGH'
        for letter in columns:
            if print_ranks_and_files is False:
                letter = " "
            print(letter, end=" " * h_spacing)
        print()

        # print top board border
        print("  ", end="")
        print(border_h_end_top, end=border_top * h_spacing)
        for _ in range((7*(h_spacing+1)) + h_spacing):
            print(border_top, end="")
        print(border_top, end=border_h_end_top)
        print()

        # print pieces and spaces
        for i, row in enumerate(reversed(self._board_display)):
            # print ranks (1 - 8)
            if print_ranks_and_files is True:
                rank = 8-i
            else:
                rank = " "
            print(rank, end=" ")
            print(border_sides, end=" " * h_spacing)
            for space in row:
                print(space, end=" " * h_spacing)
            print(border_sides)

        # print bottom border
        print("  ", end="")
        print(border_h_end_bot, end=border_bottom * h_spacing)
        for _ in range((7*(h_spacing+1)) + h_spacing):
            print(border_bottom, end="")
        print(border_bottom, end=border_h_end_bot)
        print()

        # print previous move made
        if self._previous_move is not None:
            color, piece, move_from, move_to, captured_piece = self._previous_move
            # print(" ", end=" " * h_spacing)
            # print(f"Previous Turn:")
            print(" ", end=" " * h_spacing)
            # print("    ", end="")  # indent
            print(f"{color} {piece} from {move_from.upper()} to {move_to.upper()}")

            # print if a piece was captured
            if self._previous_move[4] is not None:
                print(" ", end=" " * h_spacing)
                # print("    ", end="")  # indent
                if color == "White":
                    print(f"Black {captured_piece} captured!\n"
                          f"         ┻━┻ ︵ ╯(°□° ╯)")
                else:
                    print(f"White {captured_piece} captured!\n"
                          f"   (╯°□°)╯︵ ┻━┻")
        else:
            # print new game message
            print(" ", end=" " * h_spacing)
            print("New game. GOOD luck.")

        # new line
        print()

        # print game state if not "UNFINISHED"
        if self._game_state[0] != 'U':
            if self._game_state[0] == "B":
                print("\n    (╯°□°)╯︵ ┻━┻    \\(°Ω°)/\n"
                      "     '.`-* BLACK WINS *`.`'\n")
            else:
                print("\n    (ﾉ◕ヮ◕)ﾉ  ┻━┻ ︵ \\(°□° \\)  \n"
                      "     '.`-* WHITE WINS *`.`'\n")


def debug_print_bb(bitboard):
    """
    Debugging tool - prints out any number input as a 8x8 bitboard.
    :param bitboard: Integer representing a 64-bit bitboard.
    :return: None.
    """
    for row in range(8):
        for col in range(8):
            bit_position = (7 - row) * 8 + col
            if bitboard & (1 << bit_position):
                print('1 ', end=' ')
            else:
                print('. ', end=' ')
        print()
    print()


def main():

    g = ChessVar()
    while g.get_game_state() == 'UNFINISHED':
        move = input(f"{g.get_player_turn()}'s move (e.g., e2e4): ").strip()
        if len(move) == 4 and move[0] in 'abcdefghABCDEFGH' and move[1] in '12345678' and \
                move[2] in 'abcdefghABCDEFGH' and move[3] in '12345678':
            if not g.make_move(move[:2], move[2:]):
                print("Invalid move. Try again.")
        else:
            print("Invalid input format. Please use the format 'e2e4' or 'E2E4'.")


if __name__ == '__main__':
    main()
