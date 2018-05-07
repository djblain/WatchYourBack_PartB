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
import time # timing the player for testing purposes
from math import pow # used to calculate max. depth of search

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
        self.time_passed = 0
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

    def evaluation(self, board, turns):
        """
        Provide a 'score' based on the input board state,
        compared with current board state

        :param board: the board to check
        :param turns: the number of turns which have passed
        :return: the calculated score - a higher value means a 'better' outcome
        """
        # yeah definitely still not happy with this :(
        a_old = 0 # allied pieces found on current board
        e_old = 0 # enemy pieces found on current board
        s = [0,8]
        score = 0.0
        # check if we're getting close to a shrink
        if turns >= 108:
            # near first shrink, highlight safe zone
            s = []
            s = [1,7]
        if turns >= 172:
            # near second shrink, highlight safe zone
            s = []
            s = [2,6]
        for c in range(8):
            for r in range(8):
                if self.board[c][r] == self.my_piece:
                    # allied piece found
                    a_old += 1
                    #score -= 1
                elif self.board[c][r] == self.op_piece:
                    # enemy piece found
                    e_old += 1
                    #score += 1
        if a_old > e_old:
            # prioritise attack
            a_worth = 0.9
        elif a_old < e_old:
            # prioritise defense
            a_worth = 1.1
        else:
            a_worth = 1.0
        a_new = 0 # allied pieces found on input board
        e_new = 0 # enemy pieces found on input board
        for c in range(8):
            for r in range(8):
                if board[c][r] == self.my_piece:
                    # allied piece found
                    a_new += 1
                    if c in range(s[0],s[1]) and r in range(s[0],s[1]):
                        score += a_worth
                        if player_functions.can_surround(board, r, c):
                            score -= 0.5
                elif board[c][r] == self.op_piece:
                    # enemy piece found
                    e_new += 1
                    if c in range(s[0],s[1]) and r in range(s[0],s[1]):
                        score -= 1
                        if player_functions.can_surround(board, r, c):
                            score += 0.5
        # differences
        #a_loss = a_old - a_new
        #e_loss = e_old - e_new
        # now do something with the found information
        if e_new <= 1 and a_new > 1:
            # win state, return an absurdly high value
            return 1000
        if e_new > 1 and a_new <= 1:
            # lose state, return an absurdly low value
            #print("Loss state found!")
            #self.print_board()
            #tmp = self.board
            #self.board = board
            #self.print_board()
            #self.board = tmp
            return -1000
        if e_new <= 1 and a_new <= 1:
            # draw state: undesirable, but better than a loss
            # return a low value, but not as low as a loss
            return -500
        # weighted 'worth' of allied and enemy pieces (multiplication factors)
        #a_weight = 5
        #e_weight = 3
        #return (-a_weight*a_loss + e_weight*e_loss)
        #return (a_new*a_weight - e_new*e_weight) #- (a_old - e_old)*1.1
        return score
        #return (a_new - a_old) + (e_old - e_new)
        #return e_loss*1.1 - a_loss

    def place(self, turns):
        """
        Have the player attempt to place a piece (during placing phase)

        :param turns: the number of turns that have occured
        :return: a tuple if valid placement occurs, None otherwise
        """
        i_r = 4
        i_c = 4
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
                            #print("Placing to defend!")
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
                        n_board = None
                        self.board[v[0]][v[1]] = self.my_piece
                        return v
                    n_board = None
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
                            #print("Placing to attack!")
                            return (nc, nr)
        # place piece
        # just randomly use a safe position
        if self.colour == 'white':
            # avoid placing near bottom of starting zone
            r_max -= 1
        else:
            # avoid placing near top of starting zone
            r_min += 1
        # keep track of attempts at avoiding an unsafe square
        # just place even if unsafe if taking too long
        a_attempts = 0
        while ((self.board[i_c][i_r] != '-' or i_r not in range(r_min, r_max))
                or ([i_c,i_r] in l_avoid and a_attempts < 10)):
            # bias placement towards center of board
            i_c = random.randrange(max(0,3-a_attempts), min(8,5+a_attempts))
            i_r = random.randrange(
                max(r_min,3-a_attempts), min(r_max,5+a_attempts))
            a_attempts += 1
        self.board[i_c][i_r] = self.my_piece
        return (i_c, i_r)

    def moves_generate(self, board, my_turn, shrinks):
        """
        Generates a list of moves that could occur next

        :param board: the board state to check
        :param my_turn: whether it is this player's turn
        :param shrinks: the number of times the board has shrunk
        :return: a list of possible moves (entry format [column,row,direction])
        """
        # first find the right pieces
        if my_turn:
            p_check = self.my_piece
        else:
            p_check = self.op_piece
        p_locations = []
        for c in range(8):
            for r in range(8):
                if board[c][r] == p_check:
                    # appropriate piece found
                    p_locations.append([c,r])
        dirs = ["left","right","up","down"]
        moves = []
        for l in p_locations:
            # now see if we can move these pieces
            for d in dirs:
                # check this direction, add it if we can move or jump
                if player_functions.can_move(board, l[1], l[0], shrinks, d):
                    moves.append([l[0], l[1], d])
                elif player_functions.can_jump(board, l[1], l[0], shrinks, d):
                    moves.append([l[0], l[1], d])
        return moves

    def move_next(self, board, my_turn, turns, alpha, beta, depth, depth_max):
        """
        Using alpha-beta pruning, find the best move to make next

        :param board: the current board state to check
        :param my_turn: whether it is this player's turn
        :param turns: how many turns into the moving phase we are
        :param alpha: the current minimum score for maximising player
        :param beta: the current maximum score for minimising player
        :param depth: how deep the search is currently
        :param depth_max: the maximum depth to search
        :return: either alpha/beta if depth > 0, otherwise a list of best moves
        """
        a, b = alpha, beta
        shrinks = player_functions.get_shrinks(turns)
        n_shrinks = player_functions.get_shrinks(turns+1)
        c_score = self.evaluation(board, turns)
        if c_score <= -500:
            # lose/draw state
            return (c_score + depth)
        if c_score > 500:
            # win state
            return (c_score - depth)
        if depth == depth_max:
            return c_score
        l_moves = self.moves_generate(board, my_turn, shrinks)
        # check that a move is possible
        if len(l_moves) == 0:
            # no moves possible
            n_board = player_functions.board_duplicate(board)
            # shrink and eliminate, if necessary
            if n_shrinks != shrinks:
                player_functions.shrink(n_board, n_shrinks)
            n_score = self.move_next(n_board, not my_turn, turns+1, alpha,
                beta, depth+1, depth_max)
            n_board = None
            return n_score
        m_best = [] # list of best moves, return if depth == 0 instead of score
        for m in l_moves:
            n_board = player_functions.board_duplicate(board)
            player_functions.move_perform(
                n_board, m[1], m[0], shrinks, m[2])
            if my_turn:
                player_functions.eliminate(
                    n_board, self.op_piece, self.my_piece)
                if shrinks != n_shrinks:
                    player_functions.shrink(n_board, n_shrinks)
                s = self.move_next(
                    n_board, False, turns+1, a, b, depth+1, depth_max)
                if s > a:
                    a = s
                    m_best.clear()
                    m_best.append(m)
                    #if depth == 0:
                    #    print(str(m) + " " + str(a))
                elif s == a:
                    m_best.append(m)
                    #if depth == 0:
                    #    print("Also: " + str(m))
            else:
                player_functions.eliminate(
                    n_board, self.my_piece, self.op_piece)
                if shrinks != n_shrinks:
                    player_functions.shrink(n_board, n_shrinks)
                s = self.move_next(
                    n_board, True, turns+1, a, b, depth+1, depth_max)
                #if depth == 1 and s < b:
                #    print("New worst: " + str(s) + str(m))
                b = min(s,b)
            if b <= a:
                break
        if depth == 0:
            return m_best
        if my_turn:
            return a
        else:
            return b

    def move(self, turns):
        """
        Have a player attempt a move, assuming one is possible

        :param turns: the number of turns into the moving phase we are
        :return: a tuple of tuples for a valid move
        """
        shrinks = player_functions.get_shrinks(turns)
        n_pieces = player_functions.pieces_count(self.board)
        d_max = 2
        t_max = 10000 # try to keep running time complexity below this
        # assume branching factor, b, equals average of total moves per team,
        # assuming all pieces can be moved in all directions
        # i.e. b = no. pieces * no. directions / no. teams = n_pieces*4/2
        while d_max < 5 and pow(n_pieces*2, d_max+1) <= t_max:
            # we can go further, increase depth
            d_max += 1
        l_moves = self.move_next(
            self.board, True, turns, -100000, 100000, 0, d_max)
        if l_moves == None:
            return None
        f_move = random.choice(l_moves)
        s_best = -10000
        for m in l_moves:
            # try to do move which is best "immediately"
            # select from list of "best" long-term moves
            n_board = player_functions.board_duplicate(self.board)
            player_functions.move_perform(n_board, m[1], m[0], shrinks, m[2])
            player_functions.eliminate(n_board, self.op_piece, self.my_piece)
            ns = self.evaluation(n_board, turns+1)
            if ns > s_best:
                # new better move
                s_best = ns
                f_move = m
            elif ns == s_best:
                # new equal best, choose randommly if we want to use
                f_move = random.choice([f_move, m])
        n_pos = player_functions.move_perform(
            self.board, f_move[1], f_move[0], shrinks, f_move[2])
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        return ((f_move[0], f_move[1]), n_pos)

    def update(self, action):
        """
        Update this player's board based on the opponent's action

        :param action: the opponent's last move
        """
        t_start = time.time()
        player_functions.update(
            self.board, action, self.my_piece, self.op_piece)
        self.time_passed += time.time() - t_start
        #print("Time (" + self.colour + "): " + str(self.time_passed) + " seconds")

    def action(self, turns):
        """
        Have the player take a turn

        :param turns: the number of turns which have passed so far
        :return: the move which occured, assuming one did
        """
        t_start = time.time()
        #print("Turn " + str(turns + 1))
        r_val = None # return value
        # know how many times board has shrunk
        shrinks = player_functions.get_shrinks(turns)
        if shrinks == 1:
            # 64 turns have passed for each player
            player_functions.shrink(self.board,shrinks)
        elif shrinks == 2:
            # 96 turns have passed for each player
            player_functions.shrink(self.board,shrinks)
        player_functions.eliminate(self.board, self.my_piece, self.op_piece)
        if self.placed < 12:
            # placing phase
            r_val = self.place(turns)
            player_functions.eliminate(self.board, self.op_piece, self.my_piece)
            self.placed += 1
        else:
            # moving phase
            # check if can do anything
            m = player_functions.moves_available(
                self.board,self.my_piece,shrinks)
            if m == 0:
                r_val = None
            else:
                r_val = self.move(turns)
        n_shrinks = player_functions.get_shrinks(turns+1)
        if n_shrinks != shrinks:
            player_functions.shrink(self.board, n_shrinks)
        #self.print_board()
        self.time_passed += time.time() - t_start
        #print("Time (" + self.colour + "): "
        #    + str(self.time_passed) + " seconds")
        return r_val

