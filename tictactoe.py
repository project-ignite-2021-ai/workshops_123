'''
This tic-tac-toe visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Tic-Tac-Toe: The game starts with an empty 3x3 board. Each turn, a
player places his piece (O for Player 1, X for Player 2) on one of
the unoccupied squares. The player that forms a row, column, or 
diagonal of 3 of his pieces is the winner.
    Eg. 
        |-----------|     |-----------|     |-----------|     |-----------|
        |   |   |   |     |   | O |   |     |   | O |   |     |   | O | O |
        |-----------|     |-----------|     |-----------|     |-----------|
        |   |   |   | --> |   |   |   | --> |   |   |   | --> |   |   |   |
        |-----------|     |-----------|     |-----------|     |-----------|
        |   |   |   |     |   |   |   |     |   |   | X |     |   |   | X |
        |-----------|     |-----------|     |-----------|     |-----------|
        
        |-----------|     |-----------|     |-----------|     |-----------|
        | X | O | O |     | X | O | O |     | X | O | O |     | X | O | O |
        |-----------|     |-----------|     |-----------|     |-----------|
    --> |   |   |   | --> |   | O |   | --> |   | O |   | --> |   | O |   |
        |-----------|     |-----------|     |-----------|     |-----------|
        |   |   | X |     |   |   | X |     |   | X | X |     | O | X | X |
        |-----------|     |-----------|     |-----------|     |-----------|
    Player 1 (O) is the winner!
'''

import pygame as pg
import random, time
from copy import deepcopy
# deepcopy is very important for creating different instances
# of the board. Otherwise, changing newBoard would change board!

black = (0,0,0)
white = (255,255,255)
blue = (0, 0, 255) # for Player 1 (O)
red = (255, 0, 0) # for Player 2 (X)
colors = [black, blue, red]

##### GUI Tools #####

def drawO(x,y):
    pg.draw.circle(screen, blue, (y*100 + 50, x*100 + 50), 40, 15)
def drawX(x,y):
    p1 = (y*100 + 25,x*100 + 20)
    p2 = (y*100 + 75,x*100 + 20)
    p3 = (y*100 + 25,x*100 + 80)
    p4 = (y*100 + 75,x*100 + 80)
    pg.draw.line(screen, red, p1, p4, 20)
    pg.draw.line(screen, red, p2, p3, 20)

def drawBoard(board):
    # draw background
    screen.fill(white)
    
    # draw lines
    pg.draw.line(screen, black, (100, 0), (100, 300), 10)
    pg.draw.line(screen, black, (200, 0), (200, 300), 10)
    pg.draw.line(screen, black, (0, 100), (300, 100), 10)
    pg.draw.line(screen, black, (0, 200), (300, 200), 10)
    
    # draw pieces
    for x in range(3):
        for y in range(3):
            B = board[x][y]
            if B==1:   drawO(x,y)
            elif B==2: drawX(x,y)
    
    # check for 3-in-a-row
    for i in range(3):
        # check rows
        piece = board[i][0]
        if piece != 0 and piece == board[i][1] \
                      and piece == board[i][2]:
            pg.draw.line(screen, colors[piece], \
                (0, i*100 + 50), (300, i*100 + 50), 15)
        
        # check columns
        piece = board[0][i]
        if piece != 0 and piece == board[1][i] \
                      and piece == board[2][i]:
            pg.draw.line(screen, colors[piece], \
                (i*100 + 50,0), (i*100 + 50, 300), 15)

    # check diagonals
    piece = board[1][1]
    if piece != 0 and piece == board[0][0] \
                  and piece == board[2][2]:
        pg.draw.line(screen, colors[piece], \
                (0,0), (300,300), 20)
    if piece != 0 and piece == board[0][2] \
                  and piece == board[2][0]:
        pg.draw.line(screen, colors[piece], \
                (0,300), (300,0), 20)

    # flip (ie. update the board)
    pg.display.flip()

def printBoard(board):
    TableTB = "|-----------|"
    print(TableTB)
    for x in range(3):
        for y in range(3):
            print("|", end='')
            B = board[x][y]
            symbol = " X " if B==2 else " O " if B==1 else "   "
            print(symbol, end='')
        print("|")
        print(TableTB)

##### Game Tools #####

# return either the piece (1 or 2) of the winning player,
# 0 if game is still ongoing, or 3 if it's a tie
def gameIsDone(board):
    for i in range(3):
        # check rows
        piece = board[i][0]
        if piece != 0 and piece == board[i][1] \
                      and piece == board[i][2]:
            return piece
        
        # check columns
        piece = board[0][i]
        if piece != 0 and piece == board[1][i] \
                      and piece == board[2][i]:
            return piece

    # check diagonals
    piece = board[1][1]
    if piece != 0 and piece == board[0][0] \
                  and piece == board[2][2]:
        return piece
    if piece != 0 and piece == board[0][2] \
                  and piece == board[2][0]:
        return piece
    
    # else, either game is ongoing (0) or a tie (3)
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return 0
    return 3

# given (x,y) (in terms of 2D coordinate grid),
# convert to coresponding (xb, yb), where
# board[xb][yb] is the corresponding square
#          (x,y)                  (xb,yb)
#    (1,3) (2,3) (3,3)       (0,0) (0,1) (0,2)
#    (1,2) (2,2) (3,2)  -->  (1,0) (1,1) (1,2)
#    (1,1) (2,1) (3,1)       (2,0) (2,1) (2,2)
def xy_to_board(xy):
    (x, y) = xy
    return (3-y, x-1)
def board_to_xy(xbyb):
    (xb, yb) = xbyb
    return (yb+1, 3-xb)

# given (x,y) (NOT (xb,yb)), simply check if xy is open
def xy_is_valid(xy, board):
    (xb, yb) = xy_to_board(xy)
    if xb < 0 or xb > 2 or yb < 0 or yb > 2:
        return False
    if board[xb][yb] != 0:
        return False
    return True

# return list of all legal (x,y) moves on the board
def getValidMoves(board):
    validMoves = []
    for x in range(1,4):
        for y in range(1,4):
            if xy_is_valid((x,y), board):
                validMoves.append((x,y))
    return validMoves

# return a new board after Player 'turn' placing their piece at (x,y)
def updateBoard(xy, turn, board):
    assert xy_is_valid(xy, board)
    (xb, yb) = xy_to_board(xy)
    newBoard = deepcopy(board)
    newBoard[xb][yb] = turn
    return newBoard

##### Player 1's and 2's Strategies #####
# turn = current turn (1 or 2)
# board = current Tic-Tac-Toe board
# return position of where to place piece

def BuildBlockStrat(turn, board):
    # Build-And-Block Strategy - simple single-depth strategy.
    # 3 priorities are presented in order
    validMoves = getValidMoves(board)
    
    # 1. if placing a piece will win the game, place it
    for move in validMoves:
        newBoard = updateBoard(move, turn, board)
        if gameIsDone(newBoard):
            return move
    
    # 2. if opponent is able to place a 3rd piece in a row and win the game
    # next turn, block by putting a piece there. (However, can't do anything 
    # if opponent can win at another location as well)
    oppturn = 2 if turn==1 else 1
    for move in validMoves:
        newBoard = updateBoard(move, oppturn, board)
        if gameIsDone(newBoard):
            return move
    
    # 3. play any random move
    return random.choice(validMoves)


# use simple minimax (no pruning) up to depth 'depth'
def MinimaxStrat(depth, turn, board):
    [x, y, _] = minimax(depth, turn, turn, board)
    return (x,y)

# Inputs:
#     depth = max depth that we'll run minimax
#     turn = turn of the player who called MinimaxStrat
#     curTurn = turn of the current minimax node
#     board = current board
# Outputs:
#     best = [best x, best y, score after reaching (best x, best y)]
def minimax(depth, turn, curTurn, board): # TODO
    
    # Helpful Functions:
    # gameIsDone(board): return 0 if game isn't over, 1 if Player 1 wins,
    #      2 if Player 2 wins, and 3 if it's a tie
    # getValidMoves(board): get the valid moves given the current board
    #      state. Note that it's the same, regardless of whether you're
    #      Player 1 or Player 2.
    # updateBoard((x,y), curTurn, board): return the updated board after 
    #      Player 'curTurn' makes the move (x,y)
    
    # First check for an end state (ie. win, draw, max depth)
    # If so, return best = [-1,-1,score], where score is 0, +1, or -1

    

    # I (Player 'turn') want to maximize my score.
    # Our opponent wants to minimize my score.
    # Compare curTurn and turn to decide initial values for 'best'

    

    # For every valid move:
    #    Update the board
    #    Call minimax (recursion!) with the updated parameters (including
    #    changing curTurn b/c it's now the other player's turn)
    #    If the returned 'best' from minimax is better than our
    #        current 'best', update our 'best' (note that 'better'
    #        depends on whether we're playing as ourselves or as 
    #        our opponent!)
    


    # Return our best
    return best


# use minimax with alpha-beta pruning up to depth 'depth'
def MinimaxPruningStrat(depth, turn, board):
    [x, y, _] = mmpruning(depth, turn, turn, -100, +100, board)
    return (x,y)

# Inputs:
#     depth = max depth that we'll run minimax
#     turn = turn of the player who called MinimaxStrat
#     curTurn = turn of the current minimax node
#     alpha = largest reachable score by us
#     beta = smallest reachable score by opponent
#     board = current board
# Outputs:
#     best = [best x, best y, score after reaching (best x, best y)]
def mmpruning(depth, turn, curTurn, alpha, beta, board): # TODO
    
    # This should be exactly the same as the minimax() function,
    # except after you compare the 'best' in the for loop:
    #    if it's my turn (Player 'turn'), update alpha (the max score),
    #    and if alpha >= beta, break the for loop
    #    if it's my opponent's turn, update beta (the min score),
    #    and if alpha >= beta, break the for loop






    return best

def ConsoleStrat():
    # Console Strategy - get user input from the console/terminal
    while(True):
        try:
            # You can either split by commas or by spaces (or both!)
            # You can add parantheses too (but will be ignored)
            taken = input().strip()
            for char in ['(', ')']:
                taken = taken.replace(char, '')
            test1 = taken.split(",")
            test2 = taken.split()

            if len(test1) == 2:   taken = test1
            elif len(test2) == 2: taken = test2
            elif len(taken) == 2:
                return (int(taken[0]), int(taken[1]))
            else:
                print("Not a valid input")
                continue
            
            x = int(taken[0].strip())
            y = int(taken[1].strip())
            return (x, y)
        except ValueError:
            print("Not a valid input")

def ScreenStrat(board):
    # Screen Strategy - click the proper square on the screen
    while(True):
        mouse_x, mouse_y = pg.mouse.get_pos()

        clicked = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                clicked = True

        if clicked:
            xpos = mouse_y//100
            ypos = mouse_x//100

            if board[xpos][ypos]==0:
                return board_to_xy((xpos, ypos))

def HumanStrat(board, screenOn):
    if screenOn: return ScreenStrat(board)
    else:        return ConsoleStrat()

# given the board, return a position (x, y) to place the next piece
def Player1Strategy(board, screenOn): # CHANGE ME!
    return HumanStrat(board, screenOn)
    # return BuildBlockStrat(1, board)
    # return MinimaxStrat(10, 1, board)
    # return MinimaxPruningStrat(10, 1, board)

def Player2Strategy(board, screenOn): # CHANGE ME!
    return HumanStrat(board, screenOn)
    # return BuildBlockStrat(2, board)
    # return MinimaxStrat(10, 2, board)
    # return MinimaxPruningStrat(10, 2, board)
    


##### Main Function #####
def main():
    global screen

    # Decide if you want pygame (True) or console (False)
    screenOn = True # CHANGE ME!
    turn = 1 # player 1 is 1 (O), player 2 is 2 (X)
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    
    if screenOn:
        pg.init()
        screen = pg.display.set_mode([300, 300])

    print("Welcome to Tic-Tac-Toe!")
    if screenOn: drawBoard(board)    
    else:        printBoard(board)
    while True:
        # Exit if X is pushed
        if screenOn:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()

        # Prompt for location of player's piece
        assert not gameIsDone(board)
        print("Player %d, where will you place your piece?" % turn)
        if turn == 1:
            (x, y) = Player1Strategy(board, screenOn)
        elif turn == 2:
            (x, y) = Player2Strategy(board, screenOn)

        # Check if valid location
        if not xy_is_valid((x, y), board):
            print("You cannot take this position. Try again.")
            continue

        # Update board, then check win condition
        board = updateBoard((x, y), turn, board)
        if screenOn: drawBoard(board)    
        else:        printBoard(board)
        if gameIsDone(board):
            break
        
        # Update turn
        turn = 2 if turn==1 else 1

    if gameIsDone(board) == 3:
        print("Game is a tie!")
    else:
        print("Player %d is the winner!" % turn)
    if screenOn:
        time.sleep(2)
    
if __name__ == "__main__":
    main()