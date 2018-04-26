#-------------------------------------------------------------------------------
# Name:        human_player.py
# Purpose:
#
# Author:      Daniel Blain and Anjana Basani
#
# Created:     20/04/2018
#-------------------------------------------------------------------------------

# a lot of functions are shared by both human and AI players,
# so they are in a separate, shared module
import player_functions
from sys import exit

def is_int(s):
    """
    Checks that an input string represents an integer

    :param s: the input string to check
    :return: True if x represents an int, False otherwise
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

class Player:
    """Class for a human player"""
    def __init__(self, colour):
        """
        Initialise a human player
        Exits program if input is invalid

        :param colour: the colour of the player, either 'black' or 'white'
        """
        self.colour = colour
        self.board = player_functions.board_init()
        self.placed = 0
        if colour == 'white':
            self.my_piece = 'O'
            self.op_piece = '@'
        elif colour == 'black':
            self.my_piece = '@'
            self.op_piece = 'O'
        else:
            # if colour invalid, abort program
            print("Invalid colour! Use 'white' or 'black'")
            exit()

    def print_board(self):
        """
        Prints the current state of the board, as this player sees it
        """
        for r in range(8):
            s = ""
            for c in range(8):
                s = s + self.board[c][r] + " "
            print(s)

    def place(self):
        """
        Have the player attempt to place a piece (during placing phase)

        :return: a tuple if valid placement occurs, None otherwise
        """
        p_in = input("Input a column and a row: ")
        # check whether the player wants to abort the program
        if p_in == "quit":
            exit()
        p_split = p_in.split()
        # check that we have two inputs
        if len(p_split) != 2:
            # not the right no. of inputs
            print("Incorrect argument count! Usage: [column] [row]")
            return None
        col = p_split[0]
        row = p_split[1]
        # check that the inputs are both integers
        if not (is_int(row) and is_int(col)):
            # one (or both) not an integer
            print("Incorrect argument types! Must both be integers")
            return None
        # check that the location is on the board
        i_r = int(row)
        i_c = int(col)
        if not player_functions.on_board(i_r, i_c):
            print("Position not on board! Allowed values: 0-7")
            return None
        # check that this player can place here
        if i_r > 5 and self.colour == 'white':
            # white player can't place here
            print("White can only place on rows 0-5")
            return None
        elif i_r < 2 and self.colour == 'black':
            # black player can't place here
            print("Black can only place on rows 2-7")
            return None
        # check whether position is available
        if not self.board[i_c][i_r] == '-':
            # position taken
            print("Non-empty space!")
            return None
        # all checks passed, place piece
        self.board[i_c][i_r] = self.my_piece
        return (i_c, i_r)

    def move(self, shrinks):
        """
        Have a player attempt a move, assuming one is possible

        :param shrinks: the number of times the board has shrunk
        :return: a tuple of tuples for a valid move, or None if input invalid
        """
        # get valid piece co-ordinates first
        p_in = input("Input column and row of piece to move: ")
        # check whether the player wants to abort the program
        if p_in == "quit":
            exit()
        elif p_in == "print":
            self.print_board()
        p_split = p_in.split()
        # check that we have two inputs
        if len(p_split) != 2:
            # not the right no. of inputs
            print("Incorrect argument count! Usage: [column] [row]")
            return None
        col = p_split[0]
        row = p_split[1]
        # check that the inputs are both integers
        if not (is_int(row) and is_int(col)):
            # one (or both) not an integer
            print("Incorrect argument types! Must both be integers")
            return None
        # check that the location is on the board
        i_r = int(row)
        i_c = int(col)
        if not player_functions.on_board(i_r, i_c, shrinks):
            print("Position not on board! Allowed values: " + str(shrinks) +
                "-" + str(7-shrinks))
            return None
        # check that it's a player's piece
        if self.board[i_c][i_r] != self.my_piece:
            print("Player's piece isn't here!")
            return None
        a_directions = ["left","right","up","down"] # allowed direction inputs
        direction = input("Input a direction (left, right, up, down): ")
        if direction == "quit":
            # player want to abort program
            exit()
        if direction not in a_directions:
            # not a valid direction
            print("Invalid direction! Must be in " + str(a_directions))
            return None
        # check if movement or jumping possible
        m = player_functions.can_move(self.board,i_r,i_c,shrinks,direction)
        j = player_functions.can_jump(self.board,i_r,i_c,shrinks,direction)
        if m is not None:
            # can move
            board = player_functions.piece_move(self.board,i_r,i_c,direction)
            o = m
        elif j is not None:
            # can't move, can jump
            board = player_functions.piece_jump(self.board,i_r,i_c,direction)
            o = j
        else:
            # invalid move
            print("Cannot move this piece in this direction!")
            return None
        # movement occured, yay
        return ((i_c, i_r), o)


    def update(self, action):
        """
        Update this player's board based on the opponent's action

        :param action: the opponent's last move
        """
        self.board = player_functions.update(self.board,
            action, self.my_piece, self.op_piece)

    def action(self, turns):
        """
        Have the player take a turn

        :param turns: the number of turns which have passed so far
        :return: the move which occured, assuming one did
        """
        #print("Turn " + str(turns + 1))
        r_val = None # return value
        turn_valid = False
        # know how many times board has shrunk
        shrinks = 0
        if turns >= 128:
            shrinks += 1
            # update corner locations
            for p in [[1,1],[1,6],[6,1],[6,6]]:
                self.board[p[1]][p[0]] = 'X'
        if turns >= 192:
            shrinks += 1
            # update corner locations
            for p in [[2,2],[2,5],[5,2],[5,5]]:
                self.board[p[1]][p[0]] = 'X'
        if shrinks > 0:
            # update outside region
            for r in range(8):
                for c in range(8):
                    if (r < shrinks or c < shrinks or r > 8-shrinks
                            or c > 8-shrinks):
                        self.board[c][r] = '='
        while not turn_valid:
            # have the player attempt a move
            print('-'*32)
            if self.placed < 12:
                # placing phase
                print("Placing phase for " + self.colour + " player")
                move = self.place()
                if move is None:
                    print("Bad attempt! Try again")
                else:
                    print("Placement by " + self.colour + " at position (" +
                        str(move[0]) + ", " + str(move[1]) + ")")
                    r_val = move
                    self.placed += 1
                    turn_valid = True
            else:
                # moving phase
                # check if can do anything
                m = player_functions.moves_available(
                    self.board,self.my_piece,shrinks)
                print("Moving phase for " + self.colour + " player")
                print("Can make " + str(m) + " move(s)")
                if m == 0:
                    print("Can't make any moves!")
                    turn_valid = True
                    r_val = None
                else:
                    move = self.move(shrinks)
                    if move is None:
                        print("Bad attempt! Try again")
                    else:
                        print("Moved from " + str(move[0]) + " to " +
                            str(move[1]))
                        r_val = move
                        turn_valid = True
            print('-'*32)
        board = player_functions.eliminate(
            self.board, self.op_piece, self.my_piece)
        return r_val
