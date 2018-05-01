#-------------------------------------------------------------------------------
# Name:         ai_player.py
# Purpose:      An AI player agent that attempts to play a 'good' game of
#               'Watch Your Back'
#
# Author:       Daniel Blain and Anjana Basani
#
# Created:      01/05/2018
#-------------------------------------------------------------------------------

import player_functions
from sys import exit
import random # need these to handle randomness

class Player:
    """Class for a 'good' AI player which behaves intelligently"""
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
        random.seed() # 'randomise' the seed

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
        i_r = 0
        i_c = 0
        while True:
            #TODO: implement
            break
        # place piece
        self.board[i_c][i_r] = self.my_piece
        return (i_c, i_r)

    def move(self, shrinks):
        """
        Have a player attempt a move, assuming one is possible

        :param shrinks: the number of times the board has shrunk
        :return: a tuple of tuples for a valid move, or None if input invalid
        """
        # get locations of my pieces first
        l_pieces = []
        for r in range(8):
            for c in range(8):
                # found own piece, note its location
                if self.board[c][r] == self.my_piece:
                    l_pieces.append([r,c])
        # list of directions
        directions = ["left","right","up","down"]
        while True:
            #TODO: implement
            break
        # movement occured, yay
        return ((p[1], p[0]), m)


    def update(self, action):
        """
        Update this player's board based on the opponent's action

        :param action: the opponent's last move
        """
        player_functions.update(
            self.board,action, self.my_piece, self.op_piece)

    def action(self, turns):
        """
        Have the player take a turn

        :param turns: the number of turns which have passed so far
        :return: the move which occured, assuming one did
        """
        #print("Turn " + str(turns + 1))
        r_val = None # return value
        # know how many times board has shrunk
        shrinks = 0
        if int(turns/2) == 64:
            # 64 turns have passed for each player
            shrinks = 1
            player_functions.shrink(self.board,shrinks)
        elif int(turns/2) == 96:
            # 96 turns have passed for each player
            shrinks = 2
            player_functions.shrink(self.board,shrinks)
#        print('-'*32)
        if self.placed < 12:
            # placing phase
#            print("Placing phase for " + self.colour + " player")
            r_val = self.place()
#            print("Placement by " + self.colour + " at position (" +
#                str(r_val[0]) + ", " + str(r_val[1]) + ")")
            self.placed += 1
        else:
            # moving phase
            # check if can do anything
            m = player_functions.moves_available(
                self.board,self.my_piece,shrinks)
#            print("Moving phase for " + self.colour + " player")
#            print("Can make " + str(m) + " move(s)")
            if m == 0:
#                print("Can't make any moves!")
                r_val = None
            else:
                r_val = self.move(shrinks)
#                print("Moved from " + str(r_val[0]) + " to " +
#                    str(r_val[1]))
#        print('-'*32)
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        #player_functions.print_board(self.board)
        return r_val

