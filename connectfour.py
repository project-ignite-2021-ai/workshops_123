'''
This Connect 4 game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Connect Four: The game begins with an empty board with 6 rows and 7
columns. Each turn, a player drops 1 of his pieces (Player 1 is red,
Player 2 is yellow) in one of the columns, and that piece either falls
down to the last row or to the row above the highest piece already in that
column. The player to form 4 of their pieces in a row, column, or diagonal
wins the game.

Code is very large copied from
https://www.leaseweb.com/labs/2014/01/python-connect4-ai-mtdf-algorithm/
(though several nuances were made to fit the structure of my previous
AI game programs), and there are several helpful video tutorials on
https://www.youtube.com/watch?v=UYgyRArKDEs&list=PLFCB5Dp81iNV_inzM-R9AKkZZlePCZdtV&ab_channel=KeithGalli
'''

# import pygame as pg # apparently Python2 doesn't know pygame!
import numpy as np
import math, random, sys
# from tkinter import *
from tkinter import Tk, Button, Frame, Canvas
from copy import deepcopy
from time import time
 
# unlike the previous games, we're going to design make this board
# using Python classes, which will allow us to organize our algorithm
# functions and GUI functions better

class Board:
    '''
    Board Representation:
            x=0 x=1 x=2 x=3 x=4 x=5 x=6
        y=0  .   .   .   .   .   .   .
        y=1  .   .   .   .   .   .   .
        y=2  .   .   .   .   .   .   .
        y=3  .   .   .   .   .   .   .
        y=4  .   .   .   .   .   .   .
        y=5  .   .   .   .   .   .   .
    '''
 
    # dictionary of the tree nodes. Given the current 
    # board+depth+upper/lower, returns the upper/lower bounds
    # for the true minimax value
    # this will be our transposition table for recalling repeated
    # states/positions
    nodes = {}
 
    def __init__(self,other=None):
        self.player = 'X'   # represent the current player's piece
        self.opponent = 'O' # represent the other player's piece
        self.empty = '.'    # represent no piece
        self.width = 7
        self.height = 6
        self.fields = {}    # dictionary: position (x,y) to piece 'X','O','.'
        for y in range(self.height):
            for x in range(self.width):
                self.fields[x,y] = self.empty
        # copy constructor
        if other:
            self.__dict__ = deepcopy(other.__dict__)
 
    # Get new board after turn player puts piece in column x
    def move(self,x):
        board = Board(self)
        for y in range(board.height):
            if board.fields[x,y] == board.empty:
                board.fields[x,y] = board.player
                break
        # Turn player and opponent switch!
        board.player,board.opponent = board.opponent,board.player
        return board
 
    # Score the current position for turn player
    def __heuristic(self):
        return self.__heuristic_score(self.player)-self.__heuristic_score(self.opponent)
 
    # Score the current position for given player
    def __heuristic_score(self, player):
        lines = self.__winlines(player)
        winpositions = self.__winpositions(lines,player)
        score = 0
        # for every (x,y) position is a winning position, increase 
        # the score by (height-y) times 100
        for x in range(self.width):
            for y in range(self.height-1,0,-1):
                win = winpositions.get("{0},{1}".format(x,y),False)
                below = winpositions.get("{0},{1}".format(x,y-1),False)
                if win and below:
                    score += (self.height-y)*100
        # for every (x,y) in a winning line, increase the score by 
        # pieces * heightscore
        # pieces = number of player pieces in the winning lines
        # heightscore = 6 - average height of the empty squares of the
        #      winning lines
        for line in lines:
            pieces = 0
            height = []
            for x,y in line:
                if self.fields[x,y] == player:
                    pieces += 1
                elif self.fields[x,y] == self.empty:
                    height.append(y)
            heightscore = self.height - int(sum(height) / float(len(height)))
            score += pieces*heightscore
        return score

    # return the positions that are winning for the given player
    # ie. immediately create a 4-in-a-row
    def __winpositions(self, lines, player):
        lines = self.__winlines(player)
        winpositions = {}
        for line in lines:
            pieces = 0
            empty = None
            for x,y in line:
                if self.fields[x,y] == player:
                    pieces += 1
                elif self.fields[x,y] == self.empty:
                    if not empty == None:
                        break
                empty = (x,y)
            if pieces==3:
                winpositions["{0},{1}".format(x,y)]=True
        return winpositions
 
    # return all possible current or futures 4-in-a-rows for this player
    # lines is a list of ≥4 (x,y) positions that make a 4-in-a-row
    def __winlines(self, player):
        lines = []
        # horizontal
        for y in range(self.height):
            winning = []
            for x in range(self.width):
                if self.fields[x,y] == player or self.fields[x,y] == self.empty:
                    winning.append((x,y))
                    if len(winning) >= 4:
                        lines.append(winning[-4:])
                else:
                    winning = []
        # vertical
        for x in range(self.width):
            winning = []
            for y in range(self.height):
                if self.fields[x,y] == player or self.fields[x,y] == self.empty:
                    winning.append((x,y))
                    if len(winning) >= 4:
                        lines.append(winning[-4:])
                else:
                    winning = []
        # diagonal
        winning = []
        for cx in range(self.width-1):
            sx,sy = max(cx-2,0),abs(min(cx-2,0))
            winning = []
            for cy in range(self.height):
                x,y = sx+cy,sy+cy
                if x<0 or y<0 or x>=self.width or y>=self.height:
                    continue
                if self.fields[x,y] == player or self.fields[x,y] == self.empty:
                    winning.append((x,y))
                    if len(winning) >= 4:
                        lines.append(winning[-4:])
                else:
                    winning = []
        # other diagonal
        winning = []
        for cx in range(self.width-1):
            sx,sy = self.width-1-max(cx-2,0),abs(min(cx-2,0))
            winning = []
            for cy in range(self.height):
                x,y = sx-cy,sy+cy
                if x<0 or y<0 or x>=self.width or y>=self.height:
                    continue
                if self.fields[x,y] == player or self.fields[x,y] == self.empty:
                    winning.append((x,y))
                    if len(winning) >= 4:
                        lines.append(winning[-4:])
                else:
                    winning = []
        # return
        return lines
 
    # run mtdf from depth=1 to depth=10, but abort and return 
    # best score after 'think' seconds
    # - actual function time may be much longer
    def __iterative_deepening(self,think):
        g = (3,None)
        start = time()
        for d in range(1,10):
            g = self.__mtdf(g, d)
            if time()-start>think:
                break
        return g
 
    # MTD(f): narrow down the upper and lower bounds of the true
    # minimax value
    def __mtdf(self, g, d):
        upperBound = +1000
        lowerBound = -1000
        best = g
        while lowerBound < upperBound:
            if g[0] == lowerBound:  beta = g[0]+1
            else:                   beta = g[0]
            g = self.__minimax(True, d, beta-1, beta)
            if g[1]!=None:
                best = g
            if g[0] < beta:  upperBound = g[0]
            else:            lowerBound = g[0]
        return best
 
    # Minimax w/ ...
    # - alpha-beta pruning
    # - horizon 'depth'
    # - transposition table (lowerBound and upperBound were stored 
    #   in Board.nodes as a dictionary, with the board (as a string)
    #   + the current depth + lower/upper as the key)
    def __minimax(self, player, depth, alpha, beta):
        # fetch the stored upper and loawer bounds from the
        # transposition table, if possible
        lower = Board.nodes.get(str(self)+str(depth)+'lower',None)
        upper = Board.nodes.get(str(self)+str(depth)+'upper',None)
        if lower != None:
            if lower >= beta:
                return (lower,None)
            alpha = max(alpha,lower)
        if upper != None:
            if upper <= alpha:
                return (upper,None)
            beta = max(beta,upper)
        # if the game is over and a player has won, they get 999 points
        if self.won():
            if player:  return (-999,None)
            else:       return (+999,None)
        # if the game is over and no one has won, players get 0 points
        elif self.tied():
            return (0,None)
        # at the max depth, evaluate the state w/ the heuristic function
        elif depth==0:
            return (self.__heuristic(),None)
        # during a player's turn, make a legal move in one of the columns
        # and call minimax again. Update alpha or beta, and prune
        # appropriately.
        elif player:
            best = (alpha,None)
            for x in range(self.width):
                if self.fields[x,self.height-1]==self.empty:
                    value = self.move(x).__minimax(not player,depth-1,best[0],beta)[0]
                    if value>best[0]:
                        best = value,x
                    if value>beta:
                        break
        else:
            best = (beta,None)
            for x in range(self.width):
                if self.fields[x,self.height-1]==self.empty:
                    value = self.move(x).__minimax(not player,depth-1,alpha,best[0])[0]
                    if value<best[0]:
                        best = value,x
                    if alpha>value:
                        break
        # store the updated upper/lower bounds of this state in the
        # transposition table
        if best[0] <= alpha:
            Board.nodes[str(self)+str(depth)+"upper"] = best[0]
            Board.nodes[self.__mirror()+str(depth)+"upper"] = best[0]
        elif best[0] >= beta:
            Board.nodes[str(self)+str(depth)+"lower"] = best[0]
            Board.nodes[self.__mirror()+str(depth)+"lower"] = best[0]
        return best
 
    # best result from iterative deepening for 2 seconds
    def best(self):
        return self.__iterative_deepening(2)[1]
 
    # Determine if it's a tie yet
    def tied(self):
        for (x,y) in self.fields:
            if self.fields[x,y]==self.empty:
                return False
        return True
 
    # Get the positions of the opponent's 4-in-a-row pieces
    # in the current board, if possible
    def won(self):
        # horizontal
        for y in range(self.height):
            winning = []
            for x in range(self.width):
                if self.fields[x,y] == self.opponent:
                    winning.append((x,y))
                    if len(winning) == 4:
                        return winning
                else:
                    winning = []
        # vertical
        for x in range(self.width):
            winning = []
            for y in range(self.height):
                if self.fields[x,y] == self.opponent:
                    winning.append((x,y))
                    if len(winning) == 4:
                        return winning
                else:
                    winning = []
        # diagonal
        winning = []
        for cx in range(self.width-1):
            sx,sy = max(cx-2,0),abs(min(cx-2,0))
            winning = []
            for cy in range(self.height):
                x,y = sx+cy,sy+cy
                if x<0 or y<0 or x>=self.width or y>=self.height:
                    continue
                if self.fields[x,y] == self.opponent:
                    winning.append((x,y))
                    if len(winning) == 4:
                        return winning
                else:
                    winning = []
        # other diagonal
        winning = []
        for cx in range(self.width-1):
            sx,sy = self.width-1-max(cx-2,0),abs(min(cx-2,0))
            winning = []
            for cy in range(self.height):
                x,y = sx-cy,sy+cy
                if x<0 or y<0 or x>=self.width or y>=self.height:
                    continue
                if self.fields[x,y] == self.opponent:
                    winning.append((x,y))
                    if len(winning) == 4:
                        return winning
                else:
                    winning = []
        # default
        return None
 
    # __str__() of the symmetric board, mirrored about the middle column
    def __mirror(self):
        string = ''
        for y in range(self.height):
            for x in range(self.width):
                string+=' '+self.fields[self.width-1-x,self.height-1-y]
            string+="\n"
        return string

    # create a unique string directly from all of the piece positions
    # ('X', 'O', '.') on the board
    def __str__(self):
        string = ''
        for y in range(self.height):
            for x in range(self.width):
                string+=' '+self.fields[x,self.height-1-y]
            string+="\n"
        return string
 
class GUI:
 
    def __init__(self):
        self.app = Tk()
        self.app.title('Connect4')
        self.app.resizable(width=False, height=False)
        self.board = Board()
        self.buttons = {}
        self.frame = Frame(self.app, borderwidth=1, relief="raised")
        self.tiles = {}
        for x in range(self.board.width):
            handler = lambda x=x: self.move(x)
            button = Button(self.app, command=handler, text=x+1)
            button.grid(row=0, column=x, sticky="WE")
            self.buttons[x] = button
        self.frame.grid(row=1, column=0, columnspan=self.board.width)
        for x,y in self.board.fields:
            tile = Canvas(self.frame, width=60, height=50, bg="navy", highlightthickness=0)
            tile.grid(row=self.board.height-1-y, column=x)
            self.tiles[x,y] = tile
        handler = lambda: self.reset()
        self.restart = Button(self.app, command=handler, text='reset')
        self.restart.grid(row=2, column=0, columnspan=self.board.width, sticky="WE")
        self.update()

    # reset the board
    def reset(self):
        self.board = Board()
        self.update()
 
    # put the current player's piece in column x
    def move(self,x):
        self.app.config(cursor="watch")
        self.app.update()
        self.board = self.board.move(x)
        self.update()
        move = self.board.best()
        if move!=None:
            self.board = self.board.move(move)
            self.update()
        self.app.config(cursor="")
 
    # print the board!
    def printBoard(self):
        TableTB = "|---------------------------|"
        print(TableTB)

        for y in reversed(range(self.board.height)):
            for x in range(self.board.width):
                print("|", end='')
                B = self.board.fields[x,y]
                print(" %s " % B, end='')
            print("|")
            print(TableTB)
        
        # list the columns too!
        print("  ", end='')
        for x in range(self.board.width):
            print(x, "  ", end='')
        print()

    def update(self):
        # draw the board (in Tkinter)
        for (x,y) in self.board.fields:
            text = self.board.fields[x,y]
            if (text=='.'):
                self.tiles[x,y].create_oval(10, 5, 50, 45, fill="black", outline="blue", width=1)
            if (text=='X'):
                self.tiles[x,y].create_oval(10, 5, 50, 45, fill="red", outline="blue", width=1)
            if (text=='O'):
                self.tiles[x,y].create_oval(10, 5, 50, 45, fill="yellow", outline="blue", width=1)
        
        # print the board in the console
        self.printBoard()
        
        # configure the button states
        for x in range(self.board.width):
            if self.board.fields[x,self.board.height-1]==self.board.empty:
                self.buttons[x]['state'] = 'normal'
            else:
                self.buttons[x]['state'] = 'disabled'
        
        # if a player has won, label the 4-in-a-row
        # the only thing you can do after this is reset or quit
        winning = self.board.won()
        if winning:
            for x,y in winning:
                self.tiles[x,y].create_oval(25, 20, 35, 30, fill="black")
            for x in range(self.board.width):
                self.buttons[x]['state'] = 'disabled'

    # run the game!
    def mainloop(self):
        self.app.mainloop()
 
if __name__ == '__main__':
    GUI().mainloop()

    