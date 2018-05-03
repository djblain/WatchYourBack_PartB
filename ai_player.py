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

    def evaluation(self, board):
        """
        Provide a 'score' based on the input board state,
        compared with current board state

        :param board: the board to check
        :return: the calculated score - a higher value means a 'better' outcome
        """
        a_old = 0 # allied pieces found on current board
        e_old = 0 # enemy pieces found on current board
        for c in range(8):
            for r in range(8):
                if self.board[c][r] == self.my_piece:
                    # allied piece found
                    a_old += 1
                elif self.board[c][r] == self.op_piece:
                    # enemy piece found
                    e_old += 1
        a_new = 0 # allied pieces found on input board
        e_new = 0 # enemy pieces found on input board
        for c in range(8):
            for r in range(8):
                if board[c][r] == self.my_piece:
                    # allied piece found
                    a_new += 1
                elif board[c][r] == self.op_piece:
                    # enemy piece found
                    e_new += 1
        # differences
        a_diff = a_new - a_old
        e_diff = e_new - e_old
        # now do something with the found information
        if e_new <= 1 and a_new > 1:
            # win state, return an absurdly high value
            return 1000
        if e_new > 1 and a_new <= 1:
            # lose state, return an absurdly low value
            return -1000
        if e_new <= 1 and a_new <= 1:
            # draw state: undesirable, but better than a loss
            # return a low value, but not as low as a loss
            return -500
        # weighted 'worth' of allied and enemy pieces (multiplication factors)
        a_weight = 5
        e_weight = 3
        return (a_weight*a_diff - e_weight*e_diff)

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
                            print("Placing to attack!")
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
            i_c = random.randrange(0, 8)
            i_r = random.randrange(r_min, r_max)
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

    def move_next(self, board, my_turn, turns, alpha, beta, depth):
        """
        Using alpha-beta pruning, find the best move to make next

        :param board: the current board state to check
        :param my_turn: whether it is this player's turn
        :param turns: how many turns into the moving phase we are
        :param alpha: the current minimum score for maximising player
        :param beta: the current maximum score for minimising player
        :param depth: how many more moves ahead to check
        """
        a = alpha
        b = beta
        shrinks = player_functions.get_shrinks(turns)
        # calculate score of current board
        b_score = self.evaluation(board)
        # get list of possible moves
        l_moves = self.moves_generate(board, my_turn, shrinks)
        # check if terminal call
        if depth == 0 or b_score not in range(-250,250):
            return b_score - depth # basically avoid "quicker" loss
            # don't kamikaze, try to draw game out longer
        if my_turn:
            # maximising score
            if len(l_moves) > 0:
                s = -10000
                for m in l_moves:
                    n_board = player_functions.board_duplicate(self.board)
                    # now make the move on a temp board
                    if player_functions.can_move(
                            n_board, m[1], m[0], shrinks, m[2]):
                        player_functions.piece_move(n_board, m[1], m[0], m[2])
                    elif player_functions.can_jump(
                            n_board, m[1], m[0], shrinks, m[2]):
                        player_functions.piece_jump(n_board, m[1], m[0], m[2])
                    # eliminate pieces
                    player_functions.eliminate(
                        n_board, self.op_piece, self.my_piece)
                    # shrink, if necessary
                    if turns+1 in [128, 129]:
                        player_functions.shrink(n_board, 1)
                    elif turns+1 in [192, 193]:
                        player_functions.shrink(n_board, 2)
                    n_score = self.move_next(
                        n_board, False, turns + 1, a, b, depth-1)
                    s = max(s, n_score)
                    a = max(s, a)
                    n_board = None # clear from memory
                    if b <= a:
                        #cut-off search
                        break
                return s
            else:
                # player can't make a move
                n_board = player_functions.board_duplicate(board)
                # shrink, if necessary
                if turns+1 in [128, 129]:
                    player_functions.shrink(n_board, 1)
                elif turns+1 in [192, 193]:
                    player_functions.shrink(n_board, 2)
                return self.move_next(n_board, False, turns+1, a, b, depth-1)
        else:
            # minimising score
            if len(l_moves) > 0:
                s = 10000
                for m in l_moves:
                    n_board = player_functions.board_duplicate(self.board)
                    # now make the move on a temp board
                    if player_functions.can_move(
                            n_board, m[1], m[0], shrinks, m[2]):
                        player_functions.piece_move(n_board, m[1], m[0], m[2])
                    elif player_functions.can_jump(
                            n_board, m[1], m[0], shrinks, m[2]):
                        player_functions.piece_jump(n_board, m[1], m[0], m[2])
                    # eliminate pieces
                    player_functions.eliminate(
                        n_board, self.my_piece, self.op_piece)
                    # shrink, if necessary
                    if turns+1 in [128, 129]:
                        player_functions.shrink(n_board, 1)
                    elif turns+1 in [192, 193]:
                        player_functions.shrink(n_board, 2)
                    n_score = self.move_next(
                        n_board, True, turns + 1, a, b, depth-1)
                    s = min(s, n_score)
                    b = min(s, b)
                    n_board = None # clear from memory
                    if b <= a:
                        #cut-off search
                        break
                return s
            else:
                # player can't make a move
                n_board = player_functions.board_duplicate(board)
                # shrink, if necessary
                if turns+1 in [128, 129]:
                    player_functions.shrink(n_board, 1)
                elif turns+1 in [192, 193]:
                    player_functions.shrink(n_board, 2)
                return self.move_next(n_board, False, turns+1, a, b, depth-1)

    def move(self, turns):
        """
        Have a player attempt a move, assuming one is possible

        :param turns: the number of turns into the moving phase we are
        :return: a tuple of tuples for a valid move
        """
        # starting score
        s_begin = self.evaluation(self.board)
        # know how many shrinks have occured
        shrinks = player_functions.get_shrinks(turns)
        # get a list of possible moves first
        l_moves = self.moves_generate(self.board, True, shrinks)
        print("Can make " + str(len(l_moves)) + " moves!")
        # current best score: update as we go
        s_best = -10000
        # list of current best moves
        l_best = []
        # TODO: implement
        for m in l_moves:
            n_board = player_functions.board_duplicate(self.board)
            # now make the move on a temp board
            if player_functions.can_move(n_board, m[1], m[0], shrinks, m[2]):
                player_functions.piece_move(n_board, m[1], m[0], m[2])
            elif player_functions.can_jump(n_board, m[1], m[0], shrinks, m[2]):
                player_functions.piece_jump(n_board, m[1], m[0], m[2])
            # eliminate pieces
            player_functions.eliminate(n_board, self.op_piece, self.my_piece)
            # shrink, if necessary
            if turns+1 in [128, 129]:
                player_functions.shrink(n_board, 1)
            elif turns+1 in [192, 193]:
                player_functions.shrink(n_board, 2)
            n_score = self.move_next(
                n_board, False, turns + 1, s_best, 10000, 1+shrinks*2)
            if n_score > s_best:
                # new best score, reset list of best moves and add this one
                l_best = []
                l_best.append(m)
                s_best = n_score
            elif n_score == s_best:
                # matches best score, another possible best move
                l_best.append(m)
            else:
                print("Disregard: " + str(m))
            n_board = None # clear from memory
        # pick a "best" move randomly
        f_move = random.choice(l_best)
        if f_move is None:
            return None
        # do the move
        if player_functions.can_move(
                self.board, f_move[1], f_move[0], shrinks, f_move[2]):
            n_pos = player_functions.piece_move(
                self.board, f_move[1], f_move[0], f_move[2])
        elif player_functions.can_jump(
                self.board, f_move[1], f_move[0], shrinks, f_move[2]):
            n_pos = player_functions.piece_jump(
                self.board, f_move[1], f_move[0], f_move[2])
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        s_change = self.evaluation(self.board) - s_begin
        print("Best moves: ")
        for m in l_best:
            print(str(m))
        print("Going with: " + str(f_move))
        self.print_board()
        return ((f_move[0], f_move[1]), n_pos)

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
        shrinks = player_functions.get_shrinks(turns)
        if turns in [128, 129]:
            # 64 turns have passed for each player
            player_functions.shrink(self.board,shrinks)
            player_functions.eliminate(self.board, self.my_piece, self.op_piece)
        elif turns in [192, 193]:
            # 96 turns have passed for each player
            player_functions.shrink(self.board,shrinks)
            player_functions.eliminate(self.board, self.my_piece, self.op_piece)
        if self.placed < 12:
            r_val = self.place(turns)
            self.placed += 1
        else:
            # moving phase
            # check if can do anything
            m = player_functions.moves_available(
                self.board,self.my_piece,shrinks)
            if m == 0:
                r_val = None
            else:
                r_val = self.move(shrinks)
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        return r_val

