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

def __init__(self, colour):
    """
    Initialise a human player
    Exits program if input is invalid

    :param colour: the colour of the player, either 'black' or 'white'
    """
    self.colour = colour
    self.board = player_functions.board_init()
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

def place(self):
    """
    Have the player attempt to place a piece (during placing phase)

    :return: True if valid placement occurs, False otherwise
    """
    p_in = input("Placing phase; input a row and a column: ")
    p_split = p_in.split()
    # check that we have two inputs
    if len(p_split) != 2:
        # not the right no. of inputs
        print("Incorrect argument count! Usage: [row] [column]")
        return False
    row = p_split[0]
    col = p_split[1]
    # check that the inputs are both integers
    if not (is_int(row) and is_int(col)):
        # one (or both) not an integer
        print("Incorrect argument types! Must both be integers")
        return False
    # check that the location is on the board
    i_r = int(row)
    i_c = int(col)
    if not player_functions.on_board(i_r, i_c):
        print("Position not on board! Allowed values: 0-7")
    return True

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
    :return:
    """
    turn_valid = False
    shrinks = 0
    if turns >= 128:
        shrinks += 1
    if turns >= 192:
        shrinks += 1
    while not turn_valid:
        # have the player attempt a move
        if turns < 24:
            # placing phase
            turn_valid = self.place()
        else:
            # moving phase
