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

    def piece_eval(self, board, row, col, turns):
        """
        Evauluate the heuristic value of a piece at a given position

        :param board: the board state to check
        :param row: the row to check
        :param col: the column to check
        :param turns: the number of turns which have passed in the moving phase
        :return: the heuristic value of the piece
        """
        s_zone = [0,8] # safe zone (i.e. safe from shrinking)
        if turns >= 108:
            s_zone = [1,7]
        if turns >= 172:
            s_zone = [2,6]
        r_min = 0
        r_max = 8
        if board[col][row] == 'O':
            enemy = '@'
            r_min = 2 # enemy can't place above this
        elif board[col][row] == '@':
            enemy = 'O'
            r_max = 6 # enemy can't place below this
        else:
            return 0
        val = 100 # starting value just for existing
        # check if outside safe zone
        if (row not in range(s_zone[0],s_zone[1]) or
                col not in range(s_zone[0],s_zone[1])):
            val -= 20
        # check if surrounded here
        # shouldn't techincally be surrounded
        if player_functions.surrounded(board, row, col):
            return -50
        # the closer a piece is to the center, the more it's worth
        #if turns >= 0 or board[col][row] == self.my_piece:
        val += 20 - 2*int(max(abs(3.5-row), abs(3.5-col)))
        # if adjacent to allies, worth more
        if player_functions.piece_adjacent(board, row, col, board[col][row]):
            val += 10
        # if directly threatened by enemies, worth less
        l_vert = player_functions.can_surround_vert(board, row, col)
        if l_vert is not None:
            # next to one enemy already, see if can get surrounded by another
            if (turns >= 0):
                # moving phase
                if (player_functions.piece_adjacent(
                        board, l_vert[1], l_vert[0], enemy) or
                        player_functions.piece_jumpto(
                            board, l_vert[1], l_vert[0], enemy)):
                    val -= 30
            elif l_vert[1] in range(r_min, r_max):
                # placing phase
                val -= 500
        l_hori = player_functions.can_surround_hori(board, row, col)
        if l_hori is not None:
            # next to one enemy already, see if can get surrounded by another
            if (turns >= 0):
                # moving phase
                if (player_functions.piece_adjacent(
                        board, l_hori[1], l_hori[0], enemy) or
                        player_functions.piece_jumpto(
                            board, l_hori[1], l_hori[0], enemy)):
                    val -= 30
            elif l_hori[1] in range(r_min, r_max):
                # placing phase
                val -= 500
        #if l_hori == None and l_vert == None:
        #    val += 10
        return val

    def evaluation(self, board, turns):
        """
        Provide a 'score' based on the input board state,
        compared with current board state

        :param board: the board to check
        :param turns: the number of turns which have passed in the moving phase
        :return: the calculated score - a higher value means a 'better' outcome
        """
        allies = 0
        enemies = 0
        score = 0
        a_score = 0
        e_score = 0
        a_offset = 0
        e_offset = 0
        for c in range(8):
            for r in range(8):
                if board[c][r] == self.my_piece:
                    allies += 1
                    a_score += self.piece_eval(board, r, c, turns)
                elif board[c][r] == self.op_piece:
                    enemies += 1
                    e_score -= self.piece_eval(board, r, c, turns)
        #if allies > 0:
        #    score -= int(a_offset*20/allies)
        #if enemies > 0:
        #    score += int(e_offset*20/enemies)
        if turns >= 0:
            # into moving phase, we can win/lose/draw now
            if allies < 2 and enemies > 1:
                # loss
                return -5000
            if allies > 1 and enemies < 2:
                # win
                return 5000
            if allies < 2 and enemies < 2:
                # draw
                return -2500
        #else:
        #    print(score)
        score = a_score - e_score
        if turns >= 0:
            return score
        else:
            return a_score

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
            return self.evaluation(board, -1)
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
        p_break = False
        for c in range(8):
            for r in range(r_min, r_max):
                # place a piece
                if board[c][r] == '-':
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
                        elif s > a:
                            a = s
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
                    p_break = True
                    break
            if p_break:
                break
        if depth == 0:
            print(a)
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
        # use a-b pruning first
        #p_best = self.place_next(self.board, True, -100000, 100000, 0, 2)
        #if len(p_best) > 0:
        #    n_place = random.choice(p_best)
        #    self.board[n_place[0]][n_place[1]] = self.my_piece
        #    player_functions.eliminate(self.board, self.op_piece, self.my_piece)
        #    #self.print_board()
        #    return (n_place[0], n_place[1])
        i_r = random.randrange(3,5)
        i_c = random.randrange(3,5)
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
                        if p[1] in range(8-r_max, 8-r_min):
                            # first check whether we could defend by attacking
                            ex = 2*c-p[0]
                            ey = 2*r-p[1]
                            dx = 2*ex-c
                            dy = 2*ey-r
                            if (player_functions.on_board(dy,dx)
                                    and dy in range(r_min, r_max)):
                                if self.board[dx][dy] == '-':
                                    self.board[dx][dy] = self.my_piece
                                    self.board[ex][ey] = '-'
                                    if player_functions.can_surround(
                                            self.board, dy, dx) is not None:
                                        self.board[dx][dy] = '-'
                                        self.board[ex][ey] = self.op_piece
                                    else:
                                        self.board[ex][ey] = self.op_piece
                                        return (dx, dy)
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
                    p_surround = player_functions.can_surround(
                        n_board, v[1], v[0])
                    if (p_surround is None and player_functions.surrounded(
                            n_board,v[1],v[0]) == False):
                        # piece won't get surrounded by taking, update board
                        n_board = None
                        self.board[v[0]][v[1]] = self.my_piece
                        return v
                    elif p_surround is not None:
                        if p_surround[1] not in range(8-r_max, 8-r_min):
                            # actually safe
                            n_board = None
                            self.board[v[0]][v[1]] = self.my_piece
                            return v
                    n_board = None
        # attempt to threaten an enemy
        for e in l_enemy:
            for l in l_adjacent:
                # check if we can place here
                if (player_functions.on_board(e[1]+l[1], e[0]+l[0], 0) and
                        player_functions.on_board(e[1]-l[1], e[0]-l[0], 0)):
                    nc = e[0]+l[0]
                    nr = e[1]+l[1]
                    sc = e[0]-l[0]
                    sr = e[1]-l[1]
                    if nr in range(r_min, r_max) and self.board[nc][nr] == '-':
                        # in our starting zone and free
                        # attempt to place
                        self.board[nc][nr] = self.my_piece
                        if (player_functions.can_surround(
                                self.board, nr, nc) is not None):
                            # can get surrounded here, unsafe!
                            self.board[nc][nr] = '-'
                            l_avoid.append([nc,nr])
                        elif not player_functions.on_board(sr, sc):
                            # wouldn't be able to surround, not on board
                            self.board[nc][nr] = '-'
                            #l_avoid.append([nc,nr])
                        else:
                            # check if we actually threaten the piece
                            if (player_functions.can_surround(
                                    self.board, e[1], e[0]) is not None
                                    and sr in range(r_min, r_max)):
                                return (nc, nr)
                            else:
                                self.board[nc][nr] = '-'
                                #l_avoid.append([nc,nr])
        for e in range(1,5):
            l_positions = []
            adj_position_found = False
            for c in range(4-e,4+e):
                for r in range(4-e,4+e):
                    if r in range(r_min, r_max):
                        if self.board[c][r] == '-':
                            if [c,r] not in l_avoid:
                                adjacent = player_functions.piece_adjacent(
                                    self.board, r, c, self.my_piece)
                                if adjacent == adj_position_found:
                                    l_positions.append([c,r])
                                elif adjacent and not adj_position_found:
                                    adj_position_found = True
                                    l_positions.clear()
                                    l_positions.append([c,r])
            if len(l_positions) > 0:
                f_pos = random.choice(l_positions)
                for p in l_positions:
                    if self.colour == 'black':
                        # aim for lower positions
                        if p[1] == f_pos[1]:
                            f_pos = random.choice([p, f_pos])
                        elif p[1] > f_pos[1]:
                            f_pos = p
                    else:
                        # aim for lower positions
                        if p[1] == f_pos[1]:
                            f_pos = random.choice([p, f_pos])
                        elif p[1] < f_pos[1]:
                            f_pos = p
                self.board[f_pos[0]][f_pos[1]] = self.my_piece
                return (f_pos[0], f_pos[1])
        # place next to an allied piece, for defense
        g_pos = []
##        for c in range(8):
##            for r in range(8):
##                if self.board[c][r] == self.my_piece:
##                    for l in l_adjacent:
##                        px = c+l[0]
##                        py = r+l[1]
##                        if (player_functions.on_board(py,px)
##                                and py in range(r_min,r_max)):
##                            if self.board[px][py] == '-':
##                                self.board[px][py] = self.my_piece
##                                p = player_functions.can_surround(
##                                    self.board, py, px)
##                                if p is None:
##                                    g_pos.append([px,py])
##                                elif p[1] not in range(8-r_max, 8-r_min):
##                                    g_pos.append([px,py])
##                                self.board[px][py] = '-'
        if len(g_pos) > 0:
            place = random.choice(g_pos)
            score = -10000
            # evauluate which location is best
            for g in g_pos:
                n_board = player_functions.board_duplicate(self.board)
                n_board[g[0]][g[1]] = self.my_piece
                player_functions.eliminate(
                    n_board, self.op_piece, self.my_piece)
                n_score = self.evaluation(n_board, 0)
                if n_score > score:
                    n_score = score
                    place = g
                elif n_score == score:
                    place = random.choice([place, g])
                n_board = None
            self.board[place[0]][place[1]] = self.my_piece
            return (place[0], place[1])
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
            i_c = random.randrange(
                max(0,3-int(a_attempts/2)), min(8,5+int(a_attempts/2)))
            i_r = random.randrange(
                max(r_min,3-int(a_attempts/2)), min(r_max,5+int(a_attempts/2)))
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
                    #    print(str(m_best) + " " + str(a))
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
                if s < b:
                    b = s
            n_board = None
            if b <= a:
                break
        if depth == 0:
            #print("Best: " + str(m) + " / " +str(a))
            #print(a)
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
        shrinks = player_functions.get_shrinks(turns)
        #n_pieces = player_functions.pieces_count(self.board)
        my_moves = player_functions.moves_available(
            self.board, self.my_piece, shrinks)
        op_moves = player_functions.moves_available(
            self.board, self.op_piece, shrinks)
        # average branching factor between the two teams
        b_factor = int((my_moves+op_moves)/2+0.5)
        d_max = 2
        t_max = 12000 # try to keep running time complexity below this
        # lower allowed running time based on how long has passed in the game
        t_max = max(int(t_max - self.time_passed*50), 3000)
        # assume branching factor, b_factor, is average of total moves per team
        while d_max < min(b_factor, 8) and pow(b_factor, d_max+1) <= t_max:
            # we can go further, increase depth
            d_max += 1
        l_moves = []
        #print(type(l_moves))
        l_moves = self.move_next(
            self.board, True, turns, -100000, 100000, 0, d_max)
        if l_moves is None:
            return None
        #print(l_moves)
        s_best = -10000
        l_moves2 = []
        if d_max > 2:
            # best moves only considering next two turns (i.e. one per player)
            l_moves2 = self.move_next(
                self.board, True, turns, -100000, 100000, 0, 2)
        l_remove = []
        #print(type(l_moves))
        f_move = random.choice(l_moves)
        if len(l_moves2) > 0:
            for m in l_moves:
                # try to do move which is best "immediately"
                # select from list of "best" long-term moves
                if m not in l_moves2:
                    l_remove.append(m)
            if len(l_remove) < len(l_moves):
                while f_move in l_remove:
                    f_move = random.choice(l_moves)
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

