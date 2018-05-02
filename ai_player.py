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
import random # need this to handle randomness

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

    def evaluation(self, board, moving):
        """
        Provide a 'score' based on the input board

        :param board: the board to check
        :param moving: whether the game is in the moving phase or not
        :return: a value
        """
        a = 0 # allied pieces found
        e = 0 # enemy pieces found
        for c in range(8):
            for r in range(8):
                if board[c][r] == self.my_piece:
                    # allied piece found
                    a += 1
                elif board[c][r] == self.op_piece:
                    # enemy piece found
                    e += 1
        # now do something with the found information
        if moving:
            # in moving phase, check if win/lose state occurs
            if e <= 1 and a > 1:
                # win state, return an absurdly high value
                return 999
            if e > 1 and a <= 1:
                # lose state, return an absurdly low value
                return -999
        # return difference in number of pieces, signed
        return (a-e)

    def place(self, turns):
        """
        Have the player attempt to place a piece (during placing phase)

        :param turns: the number of turns that have occured
        :return: a tuple if valid placement occurs, None otherwise
        """
        i_r = 0
        i_c = 0
        # know range of placeable rows
        r_max = 8
        r_min = 0
        if self.colour == 'white':
            # white player
            r_max = 6
        else:
            # black player
            r_min = 2
        #TODO: implement
        # figure out a 'good' position to place a piece
        # try to first defend an endangered piece of ours
        for c in range(8):
            for r in range(8):
                if self.board[c][r] == self.my_piece:
                    # one of our pieces found
                    p = player_functions.can_surround(self.board, r, c)
                    if p is not None:
                        if (p[1] in range(r_min, r_max)
                                and self.board[p[0]][p[1]] == '-'):
                            # could get surrounded, but can defend
                            self.board[p[0]][p[1]] = self.my_piece
                            print("Placing to defend!")
                            return p
        # list of relative adjacent positions
        l_adjacent = [[-1,0],[1,0],[0,-1],[0,1]]
        # list of places to avoid placing
        # avoid placing just above/below corners
        l_avoid = [[0,1],[7,1],[0,6],[7,6]]
        # list of enemy locations
        l_enemy = []
        for c in range(8):
            for r in range(8-r_max, 8-r_min):
                if self.board[c][r] == self.op_piece:
                    # opposing piece here, add to list
                    l_enemy.append([c,r])
        # attempt to surround an enemy
        for e in l_enemy:
            v = player_functions.can_surround(self.board, e[1], e[0])
            if v is not None:
                if v[1] in range(r_min, r_max):
                    # we can surround an enemy, attempt if safe
                    n_board = player_functions.board_duplicate(self.board)
                    n_board[v[0]][v[1]] = self.my_piece
                    player_functions.eliminate(
                        n_board, self.op_piece, self.my_piece)
                    if (player_functions.can_surround(n_board, v[1], v[0])
                            is None):
                        # piece won't get surrounded by taking, update board
                        self.board[v[0]][v[1]] = self.my_piece
                        return v
        # attempt to threaten an enemy
        for e in l_enemy:
            for l in l_adjacent:
                # check if we can place here
                if player_functions.on_board(e[1]+l[1], e[0]+l[0], 0):
                    nc = e[0]+l[0]
                    nr = e[1]+l[1]
                    if nr in range(r_min, r_max) and self.board[nc][nr] == '-':
                        # in our starting zone and free
                        # attempt to place
                        self.board[nc][nr] = self.my_piece
                        if player_functions.can_surround(
                                self.board, nr, nc) is not None:
                            # can get surrounded here, unsafe!
                            self.board[nc][nr] = '-'
                            l_avoid.append([nc,nr])
                        else:
                            # safe for us, allow placement
                            print("Placing to attack!")
                            return (nc, nr)
        # place piece
        # just randomly use a safe position
        if self.colour == 'white':
            # avoid placing near bottom of strating zone
            r_max -= 1
        else:
            # avoid placing near top of starting zone
            r_min += 1
        # keep track of attempts at avoiding an unsafe square
        # just place even if unsafe if taking too long
        a_attempts = 0
        while ((self.board[i_c][i_r] != '-' or i_r not in range(r_min, r_max))
                or ([i_c,i_r] in l_avoid and a_attempts < 10)):
            i_c = random.randrange(0, 8)
            i_r = random.randrange(r_min, r_max)
            a_attempts += 1
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
            #TODO: implement (still currently random)
            d = random.choice(directions) # pick a direction
            p = random.choice(l_pieces) # pick a piece
            # attempt to move
            m = (p[1], p[0])
            if player_functions.can_move(self.board,p[0],p[1],shrinks,d):
                # can move this piece, so do it
                m = player_functions.piece_move(self.board,p[0],p[1],d)
                break
            elif player_functions.can_jump(self.board,p[0],p[1],shrinks,d):
                # can move this piece, so do it
                m = player_functions.piece_jump(self.board,p[0],p[1],d)
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
            r_val = self.place(turns)
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

