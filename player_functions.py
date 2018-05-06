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
    for i in [[0,0], [0,7], [7,0], [7,7]]:
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

def print_board(board):
    """
    Prints the current state of the input board

    :param board: the current state of the board
    """
    for r in range(8):
        s = ""
        for c in range(8):
            s = s + board[c][r] + " "
        print(s)

def on_board(row, col, shrinks=None):
    """
    Checks whether a given an indicated position is legal

    :param row: the row to check
    :param col: the column to check
    :param shrinks: the number of times the board has shrunk (default 0)
    :return: True if place valid, False otherwise
    """
    if shrinks == None:
        s = 0
    else:
        s = shrinks
    if row not in range(s,8-s):
        return False # row invalid
    if col not in range(s,8-s):
        return False # column invalid
    return True # position valid

def get_shrinks(turns):
    """
    Returns the number of shrinks which have occured so far

    :param turns: the number of turns into the moving phase
    :return: the number of shrinks which have so far occured
    """
    if turns >= 192:
        return 2
    elif turns >= 128:
        return 1
    else:
        return 0

def can_move(board, row, column, shrinks, direction):
    """
    Checks whether an indicated piece can move in the indicated direction

    :param board: the board state to check
    :param row: the row of the piece
    :param column: the column of the piece
    :param shrinks: the number of times the board has shrunk
    :param direction: the desired movement direction
    :return: True if the desired move is possible, False otherwise
    """
    if direction == "left":
        if on_board(row, column-1, shrinks):
            if board[column-1][row] == '-':
                # can move left
                return True
    elif direction == "right":
        if on_board(row, column+1, shrinks):
            if board[column+1][row] == '-':
                # can move right
                return True
    elif direction == "up":
        if on_board(row-1, column, shrinks):
            if board[column][row-1] == '-':
                # can move up
                return True
    elif direction == "down":
        if on_board(row+1, column, shrinks):
            if board[column][row+1] == '-':
                # can move down
                return True
    else:
        # cannot perform desired move
        return False

def can_jump(board, row, column, shrinks, direction):
    """
    Checks whether an indicated piece can jump in the indicated direction
    Assumes the piece will be jumping, i.e. already known to not move

    :param board: the board state to check
    :param row: the row of the piece
    :param column: the column of the piece
    :param shrinks: the number of times the board has shrunk
    :param direction: the desired jumping direction
    :return: True if the desired jump is possible, False otherwise
    """
    if direction == "left":
        if on_board(row, column-2, shrinks):
            if board[column-2][row] == '-':
                # can jump left
                return True
    elif direction == "right":
        if on_board(row, column+2, shrinks):
            if board[column+2][row] == '-':
                # can jump right
                return True
    elif direction == "up":
        if on_board(row-2, column, shrinks):
            if board[column][row-2] == '-':
                # can jump up
                return True
    elif direction == "down":
        if on_board(row+2, column, shrinks):
            if board[column][row+2] == '-':
                # can jump down
                return True
    else:
        # cannot perform desired jump
        return False

def moves_available(board, my_p, shrinks):
    """
    Counts the number of possible moves a player can perform

    :param board: the provided board state to check
    :param my_p: the piece type to check for (symbol)
    :param shrinks: the number of times the board has shrunk
    :return: the total number of moves possible
    """
    moves = 0
    directions = ["left","right","up","down"]
    for r in range(0,8):
        for c in range(0,8):
            # check each relevant piece on the board
            if board[c][r] == my_p:
                for d in directions:
                    if can_move(board,r,c,shrinks,d) is not None:
                        # a piece can move
                        moves += 1
                    elif can_jump(board,r,c,shrinks,d)is not None:
                        # a piece can jump instead
                        moves += 1
    return moves

def piece_move(board, row, col, direction):
    """
    Moves a piece in the indicated direction
    Assumes the piece can move in this direction

    :param board: the board to update
    :param row: the row of the piece to move
    :param col: the column of the piece to move
    :param direction: the direction to move the piece in
    :return: the new location, as a tuple
    """
    l = (col,row)
    if direction == "left":
        # move left
        board[col-1][row] = board[col][row]
        board[col][row] = '-'
        l = (col-1,row)
    elif direction == "right":
        # move right
        board[col+1][row] = board[col][row]
        board[col][row] = '-'
        l = (col+1,row)
    elif direction == "up":
        # move up
        board[col][row-1] = board[col][row]
        board[col][row] = '-'
        l = (col,row-1)
    elif direction == "down":
        # move down
        board[col][row+1] = board[col][row]
        board[col][row] = '-'
        l = (col,row+1)
    return l # returns new location

def piece_jump(board, row, col, direction):
    """
    Jumps a piece in the indicated direction
    Assumes the piece can jump in this direction

    :param board: the board to update
    :param row: the row of the piece to jump
    :param col: the column of the piece to jump
    :param direction: the direction to jump the piece in
    :return: the new location, as a tuple
    """
    l = (col,row)
    if direction == "left":
        # jump left
        board[col-2][row] = board[col][row]
        board[col][row] = '-'
        l = (col-2,row)
    elif direction == "right":
        # jump right
        board[col+2][row] = board[col][row]
        board[col][row] = '-'
        l = (col+2,row)
    elif direction == "up":
        # jump up
        board[col][row-2] = board[col][row]
        board[col][row] = '-'
        l = (col,row-2)
    elif direction == "down":
        # jump down
        board[col][row+2] = board[col][row]
        board[col][row] = '-'
        l = (col,row+2)
    return l # returns new position

def move_perform(board, row, col, shrinks, direction):
    """
    Performs the desired move on the input board
    Does not perform elimination or shrink

    :param board: the board to perform the move on
    :param row: the row of the piece to move
    :param col: the column of the piece to move
    :param shrinks: the number of shrinks that have occured
    :param direction: the direction the piece is moving
    :return: the new location, or None if move not possible
    """
    if can_move(board, row, col, shrinks, direction):
        return piece_move(board, row, col, direction)
    elif can_jump(board, row, col, shrinks, direction):
        return piece_jump(board, row, col, direction)
    return None

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

def can_surround(board, row, col):
    """
    Determines whether a piece could become surrounded
    To be used ONLY during placing phase
    Piece shouldn't already be surrounded!

    :param board: the board to check
    :param row: the row of the piece
    :param col: the column of the piece
    :return: a position the opponent could use to surround, or None if no such
        position is found
    """
    p = board[col][row] # piece to check
    if p not in ['O', '@']:
        return None
    if p == 'O':
        e = ['@', 'X'] # hazards for white
    else:
        e = ['O', 'X'] # hazards for black
    l_adjacent = [[-1,0],[1,0],[0,-1],[0,1]] # relative adjacent locations
    for l in l_adjacent:
        nc = l[0] + col
        nr = l[1] + row
        if on_board(nr, nc):
            # position is valid
            if board[nc][nr] in e:
                # enemy adjacent, check opposite side
                co = col - l[0]
                ro = row - l[1]
                if on_board(ro, co):
                    # opposite square valid
                    if board[co][ro] != p:
                        # not protected by ally
                        return (co, ro)
    # cannot get surrounded here
    return None

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

def shrink(board, shrinks):
    """
    Shrink the input game board

    :param board: the board to shrink
    :param shrinks: the number of times to shrink
    :return: the shrunken board
    """
    s = shrinks # short-hand
    for r in range(8):
        for c in range(8):
            # check if space now 'out of bounds'
            if r < s or c < s or r > 7-s or c > 7-s:
                # replace with arbitrary symbol (not O, @, - or X)
                board[c][r] = ':'
    # new corner locations
    n_corners = [[s,s],[s,7-s],[7-s,s],[7-s,7-s]]
    for n in n_corners:
        # place new corners
        board[n[1]][n[0]] = 'X'
    # eliminate, black gets eliminated first
    eliminate(board, 'O', '@')
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
        (y, x) = action
        board[y][x] = p_op
        eliminate(board, p_my, p_op)
    else:
        # a tuple of tuples, so a piece was moved
        ((ya, xa), (yb, xb)) = action
        board[ya][xa] = '-'
        board[yb][xb] = p_op
        eliminate(board, p_my, p_op)
    # updated!
    return board

