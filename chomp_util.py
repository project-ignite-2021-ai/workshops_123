'''
This Chomp game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

This helper file contains the classes for Board, GUI, and Player.

'''

import pygame as pg
import random
from copy import deepcopy

HALFWORD = 16 # 2 bytes
WORD = 32 # 4 bytes
QUADWORD = 64 # 8 bytes
line = (1<<QUADWORD) - 1 # 1111111...
one = 1<<(QUADWORD-1) # 1000000...
# 64 63 62 61 ... 4 3 2 1

##### Generic Helper Functions #####
def msb(n):
    return n.bit_length()-1
def lsb(n):
    return msb(n & -n)
def countSetBits(n):
    # continuously flip the last set bit until becomes 0
    count = 0
    while (n):
        n &= (n-1)
        count+= 1
    return count

# Board functions
# creates and performs functions on board arrays
class BoardFunctions:
    # Create the initial bitboard using these conventions:
    # Eg. (3,4)
    #   y=4   1   1   1
    #   y=3   1   1   1
    #   y=2   1   1   1
    #   y=1   1   1   1
    #        x=1 x=2 x=3
    def __init__(self, boardType):
        # set width and height depending on boardType
        if isinstance(boardType[0], list): # 2D matrix
            height = len(boardType)
            width = len(boardType[0])
        elif len(boardType)==2: # width x height
            width, height = boardType
        
        # check the dimensions
        if width < 1 or width > 64 or height < 1:
            print("Invalid board dimensions")
            exit()
        
        # save the dimensions
        self.width = width
        self.height = height

    # 2D board matrix or (width,height) to bitboard
    # boardType MUST be the same or derived from the initial
    # board in __init__:
    def makeBoard(self, boardType):
        if isinstance(boardType[0], list): # 2D matrix
            board = []
            for x in range(self.height):
                row = 0
                # for each bit, shift over and add value
                for y in range(self.width):
                    row = (row<<1) + boardType[x][y]
                row = row << (QUADWORD-self.width) # add the extra 0s
                board.append(row)
        elif len(boardType) == 2: # width x height
            row = line ^ ((1<<(QUADWORD-self.width)) - 1)
            board = [row for h in range(self.height)]
            
        return board

    # return an identical board
    def copyBoard(self, board):
        return deepcopy(board)

    ##### Conversions #####

    # (x,y) coordinates to [x][y] of board
    def squareToPos(self, square):
        xcoor,ycoor = square
        xpos = self.height - ycoor
        ypos = xcoor - 1
        return (xpos, ypos)

    # [x][y] of board to (x,y) coordinates
    def posToSquare(self, position):
        xpos,ypos = position
        xcoor = ypos + 1
        ycoor = self.height - xpos
        return (xcoor, ycoor)

    ##### Get and Set Specific Squares #####

    # return the square's value given (x,y) coordinates
    def getValue(self, board, square):
        xpos, ypos = self.squareToPos(square)
        return (board[xpos] >> (QUADWORD-ypos-1)) & 1

    # return the square's value given [x][y] of board
    def getPosValue(self, board, position):
        xpos, ypos = position
        return (board[xpos] >> (QUADWORD-ypos-1)) & 1
    
    # return a new board w/ square = 'value'
    def setValue(self, board, square, value):
        if not self.isOnBoard(square):
            print("Cannot set. Not on board")
            return

        board2 = self.copyBoard(board)
        xpos, ypos = self.squareToPos(square)
        if value==1:
            board2[xpos] |= (1 << (QUADWORD-ypos-1))
        elif value==0:
            board2[xpos] &= ~(1 << (QUADWORD-ypos-1))
        else:
            print("Cannot set. Invalid value")
            return None
        return board2

    # update a rectangle on the board
    # corner1 is bottomleft, corner2 is topright
    # Eg. corner1=(1,2), corner2=(3,3), value=1
    #   0 0 0 0       1 1 1 0
    #   1 1 0 0  -->  1 1 1 0
    #   1 1 0 0       1 1 0 0
    def setRectValues(self, board, corner1, corner2, value):
        if not self.isOnBoard(corner1) or \
            not self.isOnBoard(corner2):
            print("Cannot set. Not on board")
            return

        x1pos, y1pos = self.squareToPos(corner1)
        x2pos, y2pos = self.squareToPos(corner2)
        if x1pos < x2pos or y1pos > y2pos:
            print("Cannot set. Corners not in order")
            return

        board2 = self.copyBoard(board)
        at_end = (1<<(y2pos-y1pos+1)) - 1 # 00...00111
        mask = at_end<<(QUADWORD-y2pos-1) # 0011100...

        # only rows in b/w the xpos range
        for h in range(x2pos,x1pos+1):
            if value==1:
                board2[h] |= mask
            elif value==0:
                board2[h] &= ~mask
        return board2

    
    ##### Position Info #####

    # returns width of longest row (row w/ rightmost bit)
    #     1 1 1
    # Eg. 1 1   1   returns 4
    #     1
    def getMaxWidth(self, board):
        minbit = one
        for row in board:
            if row:
                lastbit = row & -row # 0010000...
                minbit = min(minbit, lastbit)
        return QUADWORD - msb(minbit)

    # returns height of tallest column
    #     1 
    #     1 1 1
    # Eg.   1 1 1   returns 4
    #     1     1
    def getMaxHeight(self, board):
        for y in range(self.height): # go down the board
            if board[y]:
                return self.height-y
        return 0

    # if board is rectangle, return widthxheight of the rectangle
    # else return None
    #     1 1 1 1
    # Eg. 1 1 1 1   returns (4,3)
    #     1 1 1 1
    def getRectangle(self, board):
        # begin by observing the last row
        lastrow = board[-1] # 1110000...
        lastbit = lastrow & -lastrow # 0010000...
        if countSetBits(lastbit) != 1:
            return None
        w = QUADWORD - msb(lastbit)

        # check the other rows and update the height
        h = 1
        for y in range(self.height-2,-1,-1): # work your way up
            if board[y] == lastrow: # part of rectangle
                h += 1
            elif board[y] == 0: # rectangle stopped
                break
            else: # not a rectangle
                return None
        return (w,h)

    # if board is L-shaped w/ thickness 1, return widthxheight of L
    # else return None
    #     1
    # Eg. 1         returns (4,3)
    #     1 1 1 1
    def getL(self, board):
        # last row
        lastrow = board[-1] # 1110000...
        lastbit = lastrow & -lastrow # 0010000...
        if countSetBits(lastbit) != 1:
            return None
        w = QUADWORD - msb(lastbit)

        # other rows
        h = 1
        for y in range(self.height-2,-1,-1):
            if board[y] == one: # part of L
                h += 1
            elif board[y] == 0: # rectangle stopped
                break
            else: # not an L
                return None
        return (w,h)

    # get a new board representing the differences b/w 2 boards
    def getDifferences(self, board1, board2):
        differences = deepcopy(board1)
        for y in range(self.height):
            differences[y] = board1[y] ^ board2[y]
        return differences

    # check if game is over
    def gameIsOver(self, board):
        for h in range(1, self.height-1):
            if board[h] != 0:
                return False
        return board[self.height-1] == one

    ##### Legal Positions #####

    # return whether or not square is w/i widthxheight
    def isOnBoard(self, square):
        xcoor, ycoor = square
        return xcoor >=1 and ycoor >=1 and \
            xcoor <= self.width and ycoor <= self.height

    # check if coordinate is valid (ie. available and not (1,1))
    def isValidMove(self, board, square):
        if square == (1,1) or not self.isOnBoard(square):
            return False
        return self.getValue(board, square)

    # get list of rows w/ at least 1 square
    def getValidRows(self, board):
        valid = []
        maxh = self.getMaxHeight(board)
        #for y in range(height-maxh, height):
        for y in range(1,maxh+1):
            if board[self.height-y] != 0:
                valid.append(y)
        return valid
    
    # get list of columns w/ at least 1 square
    def getValidCols(self, board):
        valid = []
        height = self.height
        maxh, maxw = self.getMaxHeight(board), self.getMaxWidth(board)
        allCols = 0
        for y in range(height-maxh, height):
            allCols |= board[y]
        
        # allCols (in binary) will have a 1 at a valid columns
        cursor = one
        for i in range(maxw):
            if cursor & allCols:
                valid.append(i+1)
            cursor >>= 1
        return valid

    # get list of all valid square positions on board
    def getValidMoves(self, board):
        valid = []
        # cut computation by looking at smaller range
        maxh, maxw = self.getMaxHeight(board), self.getMaxWidth(board)

        for y in range(1,maxh+1):
            for x in range(1,maxw+1):
                if x==1 and y==1:
                    continue
                if self.getValue(board, (x,y)):
                    valid.append((x,y))
        return valid

    # count number of valid moves/squares left
    def countValidMoves(self, board):
        count = 0
        maxh = self.getMaxHeight(board)
        for y in range(self.height-maxh, self.height):
            count += countSetBits(board[y])
        return count
    
    # return new board after removing the square and the
    # squares above/right. This doesn't depend on the current player
    def updateBoard(self, board, square):
        xpos, ypos = self.squareToPos(square)
        board2 = self.copyBoard(board)
        rightline = (1<<(QUADWORD-ypos)) - 1 # 0001111...
        leftline = line ^ rightline # 1110000...
        # for rows above and at current row
        for h in range(xpos+1):
            board2[h] &= leftline
        return board2


# Graphical User Interface to print or show the board
class GUI:
    white = (255,255,255)
    black = (0,0,0)
    red = (255,0,0)
    yellow = (255,255,0)
    # assume a 1920 x 1080 computer screen resolution
    sq_side = 40 # how long each square is (in pixels)
    sq_space = 10 # how much space each square needs (in pixels)

    def __init__(self, B, strat1, strat2, screenOn):
        # board set-up
        self.B = B
        self.width = B.width
        self.height = B.height

        # screen set-up
        self.screenOn = screenOn
        if strat1=='s' or strat2=='s':
            self.screenOn = True
        if screenOn:
            pg.init()
            # determine if new sq_side and sq_space are needed
            max_size = max(B.width, B.height)
            if max_size > 15 and max_size < 35:
                # for every multiple of 4, decrease by 3
                self.sq_side -= 3*(max_size // 4)
                # for every multiple of 6, decrease by 1
                self.sq_space -= 1*(max_size // 6)
            elif max_size >= 35 and max_size <= 55:
                # for every multiple of 5, decrease by 2
                self.sq_side = 16 - 2*((max_size-35) // 5)
                self.sq_space = 2
            elif max_size > 55:
                self.sq_side = 10
                self.sq_space = 1
            side = self.sq_side
            space = self.sq_space

            self.scr_width = B.width * (side+space) + space
            self.scr_height = B.height * (side+space) + space
            self.screen = pg.display.set_mode([self.scr_width, \
                                               self.scr_height])
            pg.display.set_caption('AI-m of the Game: Chomp!')

    # draw the board in the screen
    def drawBoard(self, board):
        # check if X button is clicked
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
        
        # fill screen with background color
        self.screen.fill(self.white)
        
        # draw the squares that are left
        side = self.sq_side
        space = self.sq_space
        for x in range(self.height):
            for y in range(self.width):
                # choose the proper color
                if (x,y) == self.B.squareToPos((1,1)):
                    color = self.red
                else:
                    color = self.yellow

                # note that x and y convention is flipped b/c pygame!
                #if self.B.board[x][y]:
                if self.B.getPosValue(board, (x,y)):
                    pg.draw.rect(self.screen, color, \
                        (y*(side+space)+space, x*(side+space)+space, \
                        side, side))
        pg.display.flip()

    # print the board in the console
    # assume the exact board convention as in Board class
    def printBoard(self, board):
        y = self.height
        for row in board:
            print("%2s" % y, end=' ')
            y -= 1
            cursor = one
            for col in range(self.width):
                if cursor & row:
                    print(u'\u25a0', end=' ')
                else:
                    print(' ', end=' ')
                cursor >>= 1
            print()

        print("  ", end='')
        for y in range(self.width):
            print("%2s" % (y+1), end='')
        print('\n')

    # debugging only: print the full bitboard
    def printBitBoard(self, board):
        for row in board:
            print(bin(row))
        print('\n')

# Player Strategies
class Player:
    # create Player 1 or Player 2
    def __init__(self, turn, strat):
        self.turn = turn
        self.strat = strat.lower()
        if self.strat not in ['c', 's', 'r', 'g', 'a1', 'a2']:
            print("\'%s\' HAS NOT BEEN ADDED HERE YET!!!" % self.strat)
            exit()
        
    # Given instance of Game, return a winning strategy
    def PlayerStrategy(self, G, board):
        if self.strat == 'c':
            return self.ConsoleStrat()
        elif self.strat == 's':
            return self.ScreenStrat(board, G)
        elif self.strat == 'r':
            return self.RandomStrat(board, G.B)
        elif self.strat == 'g':
            return self.GreedyStrat(board, G.B)
        elif self.strat == 'a1':
            return self.AIStrat1(board, G.B, G.Gui)
        elif self.strat == 'a2':
            return self.AIStrat2(board, G.B, G.Gui)
        
        print("\'%s\' HAS NOT BEEN ADDED HERE YET!!!" % self.strat)
        exit()

    def ConsoleStrat(self):
        # Console Strategy - get user input from the console/terminal
        # You can either split by commas or by spaces (or both!)
        # You can add parantheses too (but will be ignored)
        while(True):
            try:
                taken = input().strip()
                for char in ['(', ')']:
                    taken = taken.replace(char, '')
                test1 = taken.split(",")
                test2 = taken.split()

                if len(test1) == 2:   taken = test1
                elif len(test2) == 2: taken = test2
                else:
                    print("Not a valid input")
                    continue
                
                x = int(taken[0].strip())
                y = int(taken[1].strip())
                return (x, y)
            except ValueError:
                print("Not a valid input")

    def ScreenStrat(self, board, G):
        # Screen Strategy - click the proper square on the screen
        side = G.Gui.sq_side
        space = G.Gui.sq_space
        while(True):
            mouse_x, mouse_y = pg.mouse.get_pos()

            clicked = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    clicked = event.button==1
            
            if clicked:
                found = False
                for x in range(G.B.height):
                    for y in range(G.B.width):
                        if found:
                            break
                        # check if user clicked a square
                        rect = pg.Rect(y*(side+space)+space, \
                            x*(side+space)+space, side, side)
                        if rect.collidepoint(mouse_x, mouse_y):
                            xpos, ypos = (x,y)
                            found = True
                if not found:
                    continue

                square = G.B.posToSquare((xpos, ypos))
                if G.B.isValidMove(board, square):
                    return square
    
    def RandomStrat(self, board, B):
        # Random Strategy - return any valid move
        return random.choice(B.getValidMoves(board))

    def GreedyStrat(self, board, B):
        # Greedy Strategy - remove as many squares as possible
        # WITHOUT creating a rectangle or an L (which are almost
        # always losing for us). This is already a really good
        # strategy, but it lacks depth
        validMoves = B.getValidMoves(board)
        best = [0, None] # [no. of removed squares, move]
        for move in validMoves:
            newBoard = B.updateBoard(board, move) # make the move
            if B.gameIsOver(newBoard): # if new board is over, winning move!
                return move
            rect = B.getRectangle(newBoard)
            L = B.getL(newBoard)
            if L and L[0]==L[1]: # if an L w/ equal lengths, winning move!
                return move
            elif rect or L: # don't make a losing move!
                continue

            removed = B.getDifferences(board, newBoard) # get removed squares
            countRemoved = B.countValidMoves(removed) # count removed squares
            if countRemoved > best[0]: # if we removed the most so far ...
                best = [countRemoved, move] # ... update best
        
        if best[0] > 0: # we found a good move
            return best[1]
        else: # we couldn't find any good move
            return random.choice(validMoves)

    '''
    AIStrat1 and AIStrat2 is TODO for Teams 1 and 2 respectively.
    Return a valid move using any mathematical or AI strategies.
    You can add whatever constants or class functions you want
    (but no new classes or functions outside of this class),
    but keep ALL new changes below this comment! Please research
    Chomp and look at previous assignments before attempting this.

    Provided to you are the current board, BoardFunctions instance B, and
    GUI instance G (to print anything for debugging).

    Helpful Functions in BoardFunctions class (optimized for bitboards):
    -B.copyBoard(board): return an identical board
    -B.squareToPos(square): square coordinates -> 2D matrix positions
    -B.posToSquare(position): 2D matrix positions -> square coordinates
    
    -B.getValue(board, square): get value of square (0=empty or 1=not empty)
    -B.getPosValue(board, position): get value of 2D matrix positions
    -B.setValue(board, square, value): return new board w/ square set to value
    -B.setRectValue(board, corner1, corner2, value): return new board w/ all
        squares in rectangle formed by corner1 and corner2 (both in square
        coordinates) set to value
    
    -B.getMaxWidth(board): max width of furthest-right square
    -B.getMaxHeight(board): max height of furthest-up square
    -B.getRectangle(board): return widthxheight if board is a rectangle
    -B.getL(board): return widthxheight if board is an L-shape w/ thickness 1
    -B.gameIsOver(board): check if game is over; only (1,1) is left
    -B.getDifferences(board1, board2): return a new board where 1 represents
        the differences b/w board1 and board2
    
    -B.isOnBoard(square): check if square is w/i initial dimensions
    -B.isValidMove(board, square): check if square can be taken from board
    -B.getValidRows(board): return list of all rows w/ valid squares
    -B.getValidCols(board): return list of all columns w/ valid squares
    -B.getValidMoves(board): return list of all valid squares
    -B.updateBoard(board, square): return new board after taking away square
        and all others that are above and right of square

    Helpful Functions in GUI class:
    -Gui.printBoard(board): print the board in the console
    -Gui.printBitBoard(board): print the board as a bitboard in the console

    If you wish to add a new function to either class, please request it
    to a Project advisor first, who will then make the change.
    '''

    def AIStrat1(self, board, B, Gui):
        # AI Strategy 1 - for Team 1 to implement!




        pass

    def AIStrat2(self, board, B, Gui):
        # AI Strategy 2 - for Team 2 to implement!




        pass