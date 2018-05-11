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
from math import sqrt # used to calculate distance from center of board

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
        self.b_alpha = -10000 # the best score determined in a move
        self.b_sum = 0 # sum of beta values from possible enemy follow-up moves
        self.b_mean = 0 # mean beta value from possible enemy follow-ups
        self.predictions = [] # a list of predicted best actions for opponent
        self.op_turns = 0 # how many turns into moving phase opponent is
        self.op_optimal = 1.0 # how 'optimally' opponent has played
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

    def piece_eval(self, board, row, col, turns, my_turn):
        """
        Evauluate the heuristic value of a piece at a given position

        :param board: the board state to check
        :param row: the row to check
        :param col: the column to check
        :param turns: the number of turns which have passed in the moving phase
        :param my_turn: whether it is this player's turn at this board state
        :return: the heuristic value of the piece
        """
        shrinks = player_functions.get_shrinks(turns)
        s_zone = [0,8] # safe zone (i.e. safe from shrinking)
        if turns >= 108:
            s_zone = [1,7]
        if turns >= 172:
            s_zone = [2,6]
        r_min = 0
        r_max = 8
        if board[col][row] == 'O':
            enemy = '@'
            if turns < 0:
                r_max = 6 # can't place above this
        elif board[col][row] == '@':
            enemy = 'O'
            if turns < 0:
                r_min = 2 # can't place below this
        else:
            return 0
        # check how many enemies we are threatening
        l_adjacent = [[-1,0],[1,0],[0,-1],[0,1]]
        t_enemies = 0 # no. of enemies this piece is threatening
        for l in l_adjacent:
            dx = col + l[0]
            dy = row + l[1]
            if player_functions.on_board(dy, dx, shrinks):
                if board[dx][dy] == enemy:
                    # enemy here, is it under threat?
                    l_threat = None
                    if dx == col:
                        # same column
                        l_threat = player_functions.can_surround_vert(
                            board, dy, dx)
                    elif dy == row:
                        # same row
                        l_threat = player_functions.can_surround_hori(
                            board, dy, dx)
                    if l_threat is not None:
                        # check a piece is available to surround
                        if turns >= 0:
                            # moving phase
                            for t in l_adjacent:
                                # try a movement first
                                tx = l_threat[0] + t[0]
                                ty = l_threat[1] + t[1]
                                if player_functions.on_board(ty, tx, shrinks):
                                    if board[tx][ty] == board[col][row]:
                                        # allied piece could take!
                                        t_enemies += 1
                                        continue
                                # one can't just move there, try a jump
                                tx += t[0]
                                ty += t[1]
                                if player_functions.on_board(ty, tx, shrinks):
                                    if board[tx][ty] == board[col][row]:
                                        # make sure position doesn't refer back
                                        # to piece being evaluated
                                        if (tx != col or ty != row):
                                            # allied piece could take!
                                            t_enemies += 1
                                            continue
                        else:
                            # placing phase
                            if l_threat[1] in range(r_min,r_max):
                                t_enemies += 1
        # the closer a piece is to the center, the more it's worth
        val = 9 - int(abs(3.5-row)) - int(abs(3.5-col))
        # if we're near a shrink, proximity to center more important
        # than being threatening. Also value proximity if we're not a threat
        if (t_enemies == 0 and turns >= 0) or (turns in range(100, 128)
                or turns in range(176, 192)):
            val *= 10
            val += t_enemies
        else:
            val += 10*t_enemies
        return val

    def evaluation(self, board, turns, my_turn):
        """
        Provide a 'score' based on the input board state,
        compared with current board state

        :param board: the board to check
        :param turns: the number of turns which have passed in the moving phase
        :param my_turn: whether it is this player's turn at this board state
        :return: the calculated score - a higher value means a 'better' outcome
        """
        allies = 0
        enemies = 0
        score = 0
        a_score = 0
        e_score = 0
        for c in range(8):
            for r in range(8):
                if board[c][r] == self.my_piece:
                    allies += 1
                    a_score += self.piece_eval(board, r, c, turns, my_turn)
                elif board[c][r] == self.op_piece:
                    enemies += 1
                    e_score -= self.piece_eval(board, r, c, turns, my_turn)
        # most important: having more pieces than opponent
        # doesn't really matter how many more/less pieces we have
        # if we're far enough ahead/behind
        score += max(-400, min((allies - enemies)*100, 400))
        score += a_score - e_score
        # during moving phase, check for end-game state
        if turns >= 0:
            # into moving phase, we can win/lose/draw now
            if allies < 2 and enemies > 1:
                # loss, not preferrable
                return -5000
            if allies > 1 and enemies < 2:
                # win, always prefferable
                return 5000
            if allies < 2 and enemies < 2:
                # draw, not prefferable, except to loss
                return -2500
        # 'blur' score by opponent optimality
        # the more unpredictable the opponent, the more we should blur
        # apparant score "goodness"
        blur = int(10-9*self.op_optimal)
        score = int(score/blur + 0.5) * blur
        return score

    def place_next(self, board, my_turn, alpha, beta, depth, depth_max):
        """
        Using alpha-beta pruning, find the best move to make next

        :param board: the current board state to check
        :param my_turn: whether it is this player's placing turn
        :param alpha: the current minimum score for maximising player
        :param beta: the current maximum score for minimising player
        :param depth: how deep the search is currently
        :param depth_max: the maximum depth to search
        :return: either alpha/beta if depth > 0, otherwise a list of best places
        """
        a, b = alpha, beta
        if depth == depth_max:
            return self.evaluation(board, -1, my_turn)
        r_min = 0
        r_max = 8
        if ((my_turn == True and self.colour == 'white')
                or (my_turn == False and self.colour == 'black')):
            # white player placing
            r_max = 6
        else:
            # black player placing
            r_min = 2
        p_best = [] # list of best placements
        #p_best = None
        a_place = [] # list of placees to put pieces
        for c in range(8):
            if r_min == 2:
                # black player, start from bottom
                for r in range(7, r_min-1, -1):
                    if board[c][r] == '-':
                        a_place.append([c,r])
            else:
                # white player
                for r in range(r_max):
                    if board[c][r] == '-':
                        a_place.append([c,r])
        for p in a_place:
            c, r = p[0], p[1]
            # place a piece
            if my_turn:
                n_board = player_functions.board_duplicate(board)
                n_board[c][r] = self.my_piece
                player_functions.eliminate(
                    n_board, self.op_piece, self.my_piece)
                s = self.place_next(
                    n_board, False, a, b, depth+1, depth_max)
                n_board = None
                if s == a:
                    p_best.append([c,r])
                    #p_best = random.choice([p, p_best])
                elif s > a:
                    a = s
                    #p_best = p
                    p_best.clear()
                    p_best.append([c,r])
            else:
                n_board = player_functions.board_duplicate(board)
                n_board[c][r] = self.op_piece
                player_functions.eliminate(
                    n_board, self.my_piece, self.op_piece)
                s = self.place_next(
                    n_board, True, a, b, depth+1, depth_max)
                n_board = None
                if s < b:
                    b = s
            if b <= a:
                break
        if depth == 0:
            #print(a)
            return p_best
        if my_turn:
            return a
        else:
            return b

    def place(self, turns):
        """
        Have the player attempt to place a piece (during placing phase)

        :param turns: the number of turns that have occured
        :return: a tuple if valid placement occurs, None otherwise
        """
        # use a-b pruning
        depth = min(max(1,24-turns),2)
        p_best = self.place_next(self.board, True, -100000, 100000, 0, depth)
        n_place = random.choice(p_best)
        #n_place = p_best
        self.board[n_place[0]][n_place[1]] = self.my_piece
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        return (n_place[0], n_place[1])

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
                    dist = player_functions.dist_enemy(board, r, c)
                    # add in order of increasing distance
                    if dist != -1:
                        i = 0
                        while i < len(p_locations):
                            if dist < p_locations[i][2]:
                                p_locations.insert(i, [c,r,dist])
                                break
                            i += 1
                        if i == len(p_locations):
                            # add to end of list instead
                            p_locations.append([c,r,dist])
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
        c_score = self.evaluation(board, turns, my_turn)
        if c_score <= -2500 and depth > 0:
            # lose/draw state
            return (c_score + depth)
        if c_score > 2500 and depth > 0:
            # win state
            #if depth == 1:
            #    print("About to win!!!")
            return (c_score - depth)
        if depth == depth_max:
            return c_score
        if depth == 0 and not my_turn:
            # checking enemy best moves
            self.b_sum = 0
        l_moves = self.moves_generate(board, my_turn, shrinks)
        # check that a move is possible
        if len(l_moves) == 0:
            # no moves possible
            n_board = player_functions.board_duplicate(board)
            # shrink and eliminate, if necessary
            if n_shrinks != shrinks:
                player_functions.shrink(n_board, n_shrinks)
            n_score = self.move_next(n_board, not my_turn, turns+1, a, b,
                depth+1, depth_max)
            n_board = None
            if depth > 0:
                return n_score
            else:
                self.b_sum = n_score
                return None
        m_best = [] # list of best moves, return if depth == 0 instead of score
        for m in l_moves:
            n_board = player_functions.board_duplicate(board)
            res = player_functions.move_perform(
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
                    if depth == 0:
                        m_best.clear()
                        m_best.append(m)
                    #if depth == 0:
                    #    print(str(m_best) + " " + str(a))
                elif s == a and depth == 0:
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
                if depth == 0:
                    m_best.append(m)
                    self.b_sum += s
                if s < b:
                    b = s
            n_board = None
            if b <= a:
                break
        if depth == 0:
            if len(l_moves) > 0:
                return m_best
            else:
                return None
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
        if turns > 1:
            c_score = self.evaluation(self.board, turns, True)
            #print(c_score)
            self.op_optimal = int(self.op_optimal*self.op_turns + 0.5)
            if c_score < self.b_mean - abs(self.b_mean/10):
                # opponent playing well
                self.op_optimal += 1
            self.op_turns += 1
            self.op_optimal /= self.op_turns
            #print(self.op_optimal)
        else:
            self.op_turns += 1
        shrinks = player_functions.get_shrinks(turns)
        my_moves = player_functions.moves_available(
            self.board, self.my_piece, shrinks)
        op_moves = player_functions.moves_available(
            self.board, self.op_piece, shrinks)
        # average time to make a move
        if turns > 1:
            t_average = max(self.time_passed/int(turns/2), 0.05)
        else:
            t_average = 0.2 # one-fifth second (default for first move)
        # assume
        d_max = 2
        t_max = 20000 # try to keep running time complexity below this
        # lower allowed running time based on how long has passed in the game
        t_max = max(t_max * 0.1/t_average, 3000)
        # assume branching factor, b_factor, is average of total moves per team
        while d_max < 8 and (pow(my_moves, int((d_max+2)/2+0.5))
                * pow(op_moves, int((d_max+2)/2)) <= t_max):
            # we can go further, increase depth
            d_max += 2
        l_moves = []
        #print("Depth of search: " + str(d_max))
        l_moves = self.move_next(
            self.board, True, turns, -100000, 100000, 0, d_max)
        if l_moves is None:
            return None
        s_best = -10000
        f_move = random.choice(l_moves)
        n_pos = player_functions.move_perform(
            self.board, f_move[1], f_move[0], shrinks, f_move[2])
        player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        # try to predict next moves by opponent
        self.predictions.clear()
        op_best = self.move_next(
            self.board, False, turns+1, self.b_alpha, 10000, 0, 1)
        if type(op_best) == list:
            if len(op_best) > 1:
                self.b_mean = self.b_sum / len(op_best)
            else:
                self.b_mean = self.b_sum
        else:
            self.b_mean = self.b_sum
        #print(self.b_mean)
        #print(self.b_sum)
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
        #print("Time (" + self.colour + "): "
        #    + str(self.time_passed) + " seconds")

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
            # FOR TESTING: Force abortion!
            #exit()
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

