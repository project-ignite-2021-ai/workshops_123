'''
This Sim game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Some functions in this code are based off of
https://pythonturtle.academy/game-of-sim-with-python-turtle-source-code-included/

Sim (pencil game): The game starts with 6 dots that form a regular
hexagon. Each turn, a player creates a new edge of their color
(red for Player 1, blue for Player 2) by connecting any 2 dots with a
line, as long as a line wasn't already formed from those 2 dots.
The player who forms any triangle from 3 lines of their color LOSES.
Important: by Ramsey theory, this game cannot end in a tie!
    Eg. Hard to show in comments, see http://www.papg.com/images/Sim.gif
'''

from copy import deepcopy
import pygame as pg
import math
import random
import time

# Initialize pygame
pg.init()

# Set up the drawing window
screen = pg.display.set_mode([500, 500])

# Create a 6x6 matrix, representing all possible edges between 2 points
# Each points is represented from 0 to 5
# 0 = not taken, 1 = taken by P1, 2 = taken by P2, -1 = impossible
board = [[-1, 0, 0, 0, 0, 0], 
         [0, -1, 0, 0, 0, 0], 
         [0, 0, -1, 0, 0, 0], 
         [0, 0, 0, -1, 0, 0], 
         [0, 0, 0, 0, -1, 0], 
         [0, 0, 0, 0, 0, -1]]

# used for HumanStrat to see which dots are selected
selection = []

##### Drawing Functions #####

# which moves were made
red_edges = [] # red = Player 1
blue_edges = [] # blue = Player 2

# helpful trig shortcuts; input is degrees
def cos(angle):
    return math.cos(math.radians(angle))
def sin(angle):
    return math.sin(math.radians(angle))

# global colors for the 'turn' player (either 1 or 2)
white = (255,255,255)
black = (0,0,0)
main_color = [black, (255,0,0), (0,0,255)]
soft_color = [black, (200,0,0), (0,0,200)]
lose_color = [black, (100,100,255), (255,100,100)]


# draw a colored circle at (x,y)
def draw_dot(x,y,color):
    pg.draw.circle(screen, color, (x,y), 20)

# draw a colored circle at dots[i] (i=0,1,...,5)
def draw_dot_i(i,color):
    pg.draw.circle(screen, color, dots[i], 20)

# draw a colored line from p1 to p2
def draw_line(p1,p2,color,width):
    pg.draw.line(screen, color, p1, p2, width)
    pg.draw.circle(screen, color, p1, width/2)
    pg.draw.circle(screen, color, p2, width/2)

# get the (x,y) locations of the 6 dots on the screen
def gen_dots():
    global dots
    #     Points / dots[i] list
    #        4     5
    #
    #     3           0
    #
    #        2     1

    # since window is 500x500, center is at (250,250)
    dots = []
    radius = 150
    for angle in range(0,360,60):
        dots.append((radius*cos(angle)+250, radius*sin(angle)+250))

# given the point number (from 0 to 5), return its screen location (x,y)
def point_to_xy(p):
    return dots[p]

# given multiple point numbers, return their screen locations in (x,y)
def points_to_xy(points):
    return [dots[p] for p in points]

# draw the dots and lines on the board
def draw(turn):
    global selection

    # Fill the whole screen with a background color!
    result = gameIsDone(turn)
    if result==0:
        screen.fill(white)
    else:
        screen.fill(lose_color[turn]) # winner's color

    # Draw all the dots first
    for i in range(len(dots)):
        if i in selection: # selected a dot
            draw_dot_i(i, soft_color[turn])
        else:
            draw_dot_i(i, black)
    
    # Draw the red and blue edges, in order of appearance
    for i in range(len(red_edges)):
        # red first
        [p1,p2] = points_to_xy(red_edges[i])
        draw_line(p1, p2, main_color[1], 14)

        # then blue, if possible
        if i < len(blue_edges):
            [p1,p2] = points_to_xy(blue_edges[i])
            draw_line(p1, p2, main_color[2], 14)

    # Redraw the dots and edges of your triangle if the game is over
    if result:
        [t1,t2,t3] = getTriangle(turn)
        for i in [t1,t2,t3]:
            draw_dot_i(i, main_color[turn])
        for pair in [(t1,t2), (t1,t3), (t2,t3)]:
            [p1,p2] = points_to_xy(pair)
            draw_line(p1, p2, main_color[turn], 14)
        

    # Also draw the safe edges that don't lose the game!
    for edge in getSafeMoves(turn):
        p1 = point_to_xy(edge[0])
        p2 = point_to_xy(edge[1])
        draw_line(p1, p2, main_color[turn], 1)
    
    # Finally, flip the display
    pg.display.flip()

# print the current 2D board
def printBoard():
    for i in range(6):
        for j in range(6):
            print(board[i][j], end=' ')
        print()



##### Game Tools #####

# return list of all legal (x1,x2) moves on the current board
# note we don't need to know whose move it is
def getValidMoves():
    blank_edges = []
    for i in range(5): # 0-4
        for j in range(i,6): # 1-5
            if board[i][j] == 0:
                blank_edges.append((i,j)) # increasing order
    return blank_edges

# determine if edge (x1, x2) is valid (ie. in getValidMoves()) or not
def edge_is_valid(edge):
    [x1,x2] = edge
    return board[x1][x2] == 0

def addEdge(edge, turn):
    global board
    [x1,x2] = edge
    assert x1!=x2 and x1>=0 and x2>=0 and x1<=5 and x2<=5
    board[x1][x2] = turn
    board[x2][x1] = turn

def removeEdge(edge):
    global board
    [x1,x2] = edge
    assert x1!=x2 and x1>=0 and x2>=0 and x1<=5 and x2<=5
    board[x1][x2] = 0
    board[x2][x1] = 0

def getEdge(edge):
    [x1,x2] = edge
    return board[x1][x2]

# number of Player turn's edges attached to point p
def degree(p, turn):
    counter = 0
    for i in range(6):
        if getEdge((p,i)) == turn:
            counter += 1
    return counter

# same as degree, but for both players
def fullDegree(p):
    counter = 0
    for i in range(6):
        tmp = getEdge((p,i))
        if tmp == 1 or tmp == 2:
            counter += 1
    return counter

# return true iff there's a cycle of length 3 w/ color 'turn'
def isCycleOfThree(turn):
    for i in range(4): # 0-3
        for j in range(i+1,5): # 1-4
            if getEdge((i,j)) == turn:
                for k in range(j+1,6): #2-5
                    if getEdge((i,k)) == turn and getEdge((j,k)) == turn:
                        return True
    return False

# like isCycleOfThree(turn), but return the points that created the triangle
# assume that isCycleOfThree(turn) == True
def getTriangle(turn):
    for i in range(4): # 0-3
        for j in range(i+1,5): # 1-4
            if getEdge((i,j)) == turn:
                for k in range(j+1,6): #2-5
                    if getEdge((i,k)) == turn and getEdge((j,k)) == turn:
                        return (i,j,k)
    print("ERROR USING THIS FUNCTION!")




# return [safe, losing]
def getSafeLosingMoves(turn):
    # all losing moves are where the player's edges are on the same row
    # or column in board[][]
    
    losing = []
    for i in range(6): # for each row
        # get all edges in that row w/ board value 'turn'
        cols = [j for j in range(6) if board[i][j]==turn]
        if len(cols) > 1:
            # get all permutations of the values in cols
            for j in range(len(cols)-1):
                for k in range(j+1, len(cols)):
                    if edge_is_valid((cols[j],cols[k])):
                        x1 = cols[j]
                        x2 = cols[k]
                        losing.append( (min(x1,x2), max(x1,x2)) )
    
    safe = []
    for edge in getValidMoves():
        if edge not in losing:
            safe.append(edge)
    
    return (safe, losing)

# return list of all (x1,x2) that makes turn player lose the game
def getLosingMoves(turn):
    [_, losing] = getSafeLosingMoves(turn)
    return losing

def getLosingMoves2(turn): # too slow!
    losing = []
    for edge in getValidMoves():
        # try adding edge, and if we lose, it's a losing move
        addEdge(edge, turn)
        if isCycleOfThree(turn):
            losing.append(edge)
        removeEdge(edge)
    return losing

# the exact opposite of getLosingMoves(); returns a list of 
# moves that don't cause turn player to lose
def getSafeMoves(turn):
    [safe, _] = getSafeLosingMoves(turn)
    return safe

def getSafeMoves2(turn): # too slow!
    safe = []
    for edge in getValidMoves():
        # try adding edge, and if we don't lose, it's a safe move
        addEdge(edge, turn)
        if not isCycleOfThree(turn):
            safe.append(edge)
        removeEdge(edge)
    return safe


# return whether board is done (and if player 1 or 2 won)
# turn = turn of the player who has yet to make a move;
# return 0 if you didn't lose, return ~turn (opponent's turn)
# if you lose
def gameIsDone(turn):
    oppTurn = 2 if turn==1 else 1
    if isCycleOfThree(turn):
        return oppTurn
    return 0

# full gameIsDone(), without worrying about turn
def fullGameIsDone():
    if isCycleOfThree(1):
        return 2
    elif isCycleOfThree(2):
        return 1
    return 0


##### Player 1's and 2's Strategies #####
# no parameters; state variables are global
# return edge (x1,x2) to take


# get the intersection of 2 lists
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def RandomStrat(turn):
    # Random Strategy - simply choose a random edge
    # that doesn't lose the game (if possible)

    safe = getSafeMoves(turn)
    if safe:
        return random.choice(safe)
    # Every move loses. Just end your misery randomly.
    return random.choice(getValidMoves())

def OffensiveStrat(turn):
    # Offensive Strategy - reduce the opponent's safe moves by
    # taking one of them (if safe)

    oppTurn = 2 if turn==1 else 1
    safe = getSafeMoves(turn) # our safe moves
    oppSafe = getSafeMoves(oppTurn) # opponent's safe moves

    if safe:
        if oppSafe: # choose one of the opponent's safe moves
            return random.choice(intersection(safe, oppSafe))
        else:
            return random.choice(safe)
    
    # Every move loses. Just end your misery randomly.
    return random.choice(getValidMoves())

def DefensiveStrat(turn):
    # Defensive Strategy - avoid making edges with a dot you already
    # used. Keep track of which dots you used the least.

    safe = getSafeMoves(turn)
    if not safe:
        return random.choice(getValidMoves())

    # Count how many times each dot 0,1,...,5 was used for an edge
    dotUsage = [fullDegree(i) for i in range(6)]

    # Priorize safe edges that use dots that occur the least.
    # We do this by evaluating all safe edges and sorting them.
    scored_edges = [] # list of (dotUsage[x1] + dotUsage[x2], edge)
    for (x1, x2) in safe:
        score = dotUsage[x1] + dotUsage[x2]
        scored_edges.append((score, (x1,x2)))
    scored_edges.sort()

    # Of the edges with the smallest score, choose randomly
    min_score = scored_edges[0][0]
    best_edges = [edge for (score, edge) in scored_edges if score==min_score]
    return random.choice(best_edges)

# minimax with pruning
def MinimaxPruningStrat(depth, turn):
    [x1, x2, _] = mmpruning(depth, turn, turn, -1000, +1000)
    return (x1,x2)

# alpha = largest reachable score by us
# beta = smallest reachable score by opponent
def mmpruning(depth, turn, curTurn, alpha, beta):
    
    # return if leaf state
    over = gameIsDone(curTurn)

    # check terminal end states
    # should WIN sooner than later and LOSE later than sooner
    if over:
        if over==turn:
            score = +1+depth
        else:
            score = -1-depth
        return [-1, -1, score]
    if depth == 0:
        return [-1, -1, 0]

    nextTurn = 2 if curTurn==1 else 1

    if curTurn == turn:
        best = [-1, -1, -100]
    else:
        best = [-1, -1, +100]

    [safe, losing] = getSafeLosingMoves(curTurn)
    validMoves = safe+losing
    for edge in validMoves:
        
        # run minimax again
        addEdge(edge, curTurn)
        result = mmpruning(depth-1, turn, nextTurn, alpha, beta)
        removeEdge(edge)

        # update best
        (result[0], result[1]) = edge
        if curTurn == turn and result[2] > best[2]:
            best = result
        elif curTurn != turn and result[2] < best[2]:
            best = result

        # update alpha or beta
        if curTurn == turn:
            alpha = max(alpha, best[2])
        else:
            beta = min(beta, best[2])
        if beta <= alpha:
            break

    return best


# negamax with pruning
def NegamaxStrat(depth, turn):
    [x1, x2, _] = negamax(depth, turn, turn, 1, -1000, +1000)
    return (x1,x2)
# essentially minimax with simpler logic
def negamax(depth, turn, curTurn, color, alpha, beta):
    over = gameIsDone(curTurn)
    
    if over:
        score = +1 if over==turn else -1
        return [-1, -1, color * score]
    if depth == 0:
        return [-1, -1, 0]

    nextTurn = 2 if curTurn==1 else 1

    best = [-1, -1, -100]
    
    [safe, losing] = getSafeLosingMoves(curTurn)
    validMoves = safe+losing
    for edge in validMoves:

        # run minimax again
        addEdge(edge, curTurn)
        result = negamax(depth-1, turn, nextTurn, -color, -beta, -alpha)
        removeEdge(edge)
        
        # update best
        (result[0], result[1]) = edge
        result[2] = -result[2]
        if result[2] > best[2]:
            best = result
        
        # update alpha
        alpha = max(alpha, best[2])
        if beta <= alpha:
            break
    return best


def HumanStrat(turn):
    # Human Strategy - get user input: 2 dots that form a valid edge

    global selection

    while len(selection) < 2:
        
        x,y = pg.mouse.get_pos()
        
        clicked = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                clicked = True

        if clicked:
            for i in range(len(dots)):
                dist = (dots[i][0] - x)**2 + (dots[i][1] - y)**2
                # check if within dot/circle and not already selected
                if dist<20**2:
                    if i in selection:
                        selection.pop()
                    else:
                        selection.append(i)
                    break
        
        # redraw the dots
        draw(turn)
    
    x1x2 = (selection[0], selection[1])
    selection = []
    return x1x2


def Player1Strategy():
    # return RandomStrat(1)
    # return OffensiveStrat(1)
    # return DefensiveStrat(1)
    # return MinimaxPruningStrat(8, 1)
    # return NegamaxStrat(8, 1)
    return HumanStrat(1)

def Player2Strategy():
    # return RandomStrat(2)
    # return OffensiveStrat(2)
    # return DefensiveStrat(2)
    # return MinimaxPruningStrat(8, 2)
    # return NegamaxStrat(8, 2)
    return HumanStrat(2)


##### Main Function #####
def main():
    gen_dots()
    # points can be represented in clockwise order
    # from 0 to 5, in the following fashion:
    #     Points / dots[i] list
    #        4     5
    #
    #     3           0
    #
    #        2     1

    # draw the current Sim board
    turn = 1
    draw(turn)

    # Run until the user asks to quit
    running = True
    while running:

        # Did the user click the window close button?
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Prompt for player's new edge
        print("Player %d, select a new edge" % turn)
        if turn == 1:
            (x1, x2) = Player1Strategy()
        elif turn == 2:
            (x1, x2) = Player2Strategy()
        edge = (min(x1,x2), max(x1,x2)) # remember our ordering convention!

        # Check if valid location
        if not edge_is_valid(edge):
            print("You cannot take this edge. Try again.")
            continue

        # Update board and redraw
        addEdge(edge, turn)
        if turn == 1:
            red_edges.append(edge)
        else:
            blue_edges.append(edge)
        draw(turn)
        
        # Debugging - study the board step by step:
        # printBoard()
        # time.sleep(1)

        result = gameIsDone(turn)
        if result:
            print("Player %d is the winner!" % result)
            time.sleep(3) # change to adjust observation times
            running = False

        # Update turn
        turn = 2 if turn==1 else 1
    
    # Done! Time to quit.
    pg.quit()


if __name__ == "__main__":
    main()