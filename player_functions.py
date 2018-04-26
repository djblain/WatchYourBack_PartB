#-------------------------------------------------------------------------------
# Name:        player_functions.py
# Purpose:
#
# Author:      Daniel Blain and Anjana Basani
#
# Created:     20/04/2018
#-------------------------------------------------------------------------------

def board_init():
    """
    Initialise a board

    :return: an empty game board, as a 2D array
    """
    b = [['-' for x in range(0,8)] for y in range(0,8)]
    for i in [[0,0] [0,7] [7,0] [7,7]]:
        b[i[0]][i[1]] = 'X'

    return b

def board_duplicate(board):
    """
    Returns a duplicate of the board

    :param board: the board to duplicate
    :return: a copy of the input board
    """
    n_board = [['-' for y in range(8)] for x in range(8)]
    for r in range(8):
        for c in range(8):
            n_board[c][r] = board[c][r]
    return n_board

def on_board(row, col):
    """
    Checks whether a given an indicated position is legal

    :param row: the row to check
    :param col: the column to check
    :return: True if place valid, False otherwise
    """
    if row not in range(0,8):
        return False # row invalid
    if col not in range(0,8):
        return False # column invalid
    return True # position valid

def surrounded(board, row, col):
    """
    Checks if a piece is surrounded

    :param board: the game board to check
    :param row: the row to check
    :param col: the column to check
    :return: True if the piece at the location, False otherwise
    """
    p = board[col][row] # what type of piece this is
    # know what is 'dangerous'
    if p == 'O':
        # white piece
        e = ['@','X']
    elif p == '@':
        # black piece
        e = ['O','X']
    else:
        # not a piece
        return False
    check = [[[0,-1],[0,1]],[[-1,0],[1,0]]] # relative positions to check
    for c in check:
        a = [c[0][0]+row, c[0][1]+col] # one side
        b = [c[1][0]+row, c[1][1]+col] # other side
        if on_board(a[0], a[1]) and on_board(b[0], b[1]):
            # both positions are legal
            if board[b[1]][b[0]] in e and board[a[1]][a[0]] in e:
                # surrounded by enemies!
                return True
    # not surrounded
    return False

def eliminate(board, e_first, e_second):
    """
    Updates the given board so that pieces are eliminated correctly

    :param board: the current board state
    :param e_first: the first kind of piece to eliminate
    :param e_second: the second kind of piece to eliminate
    :return board: the updated board state
    """
    # check through pieces of type e_first first
    for r in range(0,8):
        for c in range(0,8):
            if board[c][r] == e_first:
                # right piece kind
                if surrounded(board, r, c):
                    # surrounded! delete
                    board[c][r] = '-'
    # check through pieces of type e_second after
    for r in range(0,8):
        for c in range(0,8):
            if board[c][r] == e_second:
                # right piece kind
                if surrounded(board, r, c):
                    # surrounded! delete
                    board[c][r] = '-'
    # done eliminating
    return board

def update(board, action, p_my, p_op):
    """
    Update the player's board based on the opponent's move

    :param board: the player's current board state
    :param action: the opponent's last action
    :param p_my: the character representing a piece of this player
    :param p_op: the character representing an opponent's piece
    :return: the updated board state
    """
    if action is None:
        # no action was taken previously
        return board
    elif (type(action[0]) == int):
        # a tuple of ints, so a piece was placed
        (x, y) = action
        board[y][x] = p_op
        board = eliminate(board, p_my, p_op)
    else:
        # a tuple of tuples, so a piece was moved
        ((xa, ya), (xb, yb)) = action
        board[ya][xa] = '-'
        board[yb][xb] = p_op
        board = eliminate(board, p_my, p_op)
    # updated!
    return board

