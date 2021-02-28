'''
This Chomp game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Chomp: the game begins with a rectangular grid (or something else!).
Players take turns selecting one square on the grid (except (1,1), the
bottom-leftmost square), then remove that square and all squares above
and to the right from the grid. The game ends when all squares except
(1,1) are removed, and the player who reaches this state is the winner.

Eg.        P1          P2         P1
    ■ ■ ■ (2,3) ■     (1,2)     (2,1)
    ■ ■ ■  -->  ■ ■ ■  -->       -->
    ■ ■ ■       ■ ■ ■      ■ ■ ■      ■
    Player 1 is the winner
'''

import pygame as pg
import random, time
from copy import deepcopy
from chomp_util import BoardFunctions, GUI, Player

# Board + 2 Players + GUI + Game Rules
class Game:
    # initialize the game
    def __init__(self, strat1, strat2, screenOn, boardType):
        # initial board instance
        self.B = BoardFunctions(boardType)
        self.mainboard = self.B.makeBoard(boardType)
        
        # player setup
        self.P1 = Player(1, strat1)
        self.P2 = Player(2, strat2)
        self.turn = 1 # Begin with Player 1

        # screen setup
        self.Gui = GUI(self.B, strat1, strat2, screenOn)

    # welcome the player to the game
    def welcome(self):
        print("Welcome to Chomp!")
        print("Initial board: %d by %d" % (self.B.width, self.B.height))
        if self.Gui.screenOn: self.Gui.drawBoard(self.mainboard)
        else:                 self.Gui.printBoard(self.mainboard)
    
    # change turns (done simply with binary XOR)
    def changeTurn(self):
        self.turn ^= 3

    # get a valid move from turn player
    def getMove(self):
        while(True):
            # prompt player
            print("Player %d, choose a coordinate to remove" % self.turn)
            
            # get turn player's move
            mainboard = self.B.copyBoard(self.mainboard)
            if self.turn == 1:
                square = self.P1.PlayerStrategy(self, mainboard)
            elif self.turn == 2:
                square = self.P2.PlayerStrategy(self, mainboard)

            # check if legal move
            if self.B.isValidMove(self.mainboard, square):
                return square
            else:
                print("Invalid square coordinates")
    
    # play a single person's turn
    def playTurn(self):
        # get the player's square and update board
        square = self.getMove()
        print("Player %d took away %s" % (self.turn, str(square)))
        self.mainboard = self.B.updateBoard(self.mainboard, square)

        # print the board, then check if game is over
        if self.Gui.screenOn: self.Gui.drawBoard(self.mainboard)
        else:                 self.Gui.printBoard(self.mainboard)
        
        if self.B.gameIsOver(self.mainboard):
            print("Player %d is the winner!" % self.turn)
            if self.Gui.screenOn:
                time.sleep(3) # give player time to see result
        
        # change turn
        self.changeTurn()

    # play the entire game
    def play(self):
        self.welcome()
        while not self.B.gameIsOver(self.mainboard):
            self.playTurn()


##### Custom Boards #####
custom1 = [[0,1,1,0],
           [1,1,1,1],
           [0,1,1,0],
           [1,1,1,1]]
custom2 = [[1,1,1,1,1],
           [0,1,1,1,0],
           [0,1,1,1,0],
           [0,0,1,0,0],
           [1,1,1,1,1]]
custom3 = [[0,1,1,1,0],
           [1,1,1,1,1],
           [1,0,1,0,1],
           [1,0,0,0,1],
           [1,1,1,1,1]]
custom4 = [[1,1,1,0,1],
           [1,0,1,0,1],
           [1,1,1,0,1],
           [1,0,1,0,1],
           [1,0,1,0,1]]
custom5 = [[1,1,1,1,1,1],
           [1,0,0,0,0,1],
           [1,0,1,1,0,1],
           [1,0,0,0,0,1],
           [1,1,1,1,1,1]]
custom6 = [[0,1,0,1,0,1,0,1],
           [1,0,1,0,1,0,1,0],
           [0,1,0,1,0,1,0,1],
           [1,0,1,0,1,0,1,0],
           [0,1,0,1,0,1,0,1],
           [1,0,1,0,1,0,1,0],
           [0,1,0,1,0,1,0,1],
           [1,0,1,0,1,0,1,0]]
custom7 = [[1,1,1,0,1,1,1,0,1,0,0,0,1,0,1,1,1],
           [1,0,0,0,1,0,1,0,1,1,0,1,1,0,1,0,0],
           [1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,1,1],
           [1,0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0],
           [1,1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,1]]

# Pixel Art!
custom8 = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],
           [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
           [0,0,1,1,1,0,0,1,1,1,1,0,1,0,0],
           [0,1,1,1,1,0,0,1,1,1,1,0,0,1,0],
           [0,1,1,1,1,1,1,1,1,1,1,0,0,1,0],
           [1,1,1,1,1,1,1,1,1,1,0,0,0,0,1],
           [1,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
           [1,1,1,1,1,1,1,1,0,0,0,0,0,0,1],
           [1,1,1,1,1,0,0,0,0,0,0,0,0,0,1],
           [1,1,1,1,0,0,0,0,0,0,0,0,0,0,1],
           [0,1,1,1,0,0,0,0,1,1,0,0,0,1,0],
           [0,1,1,1,0,0,0,0,1,1,0,0,0,1,0],
           [0,0,1,1,1,0,0,0,0,0,0,0,1,0,0],
           [0,0,0,1,1,1,0,0,0,0,1,1,0,0,0],
           [1,0,0,0,0,1,1,1,1,1,0,0,0,0,0]]
custom9 = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],
           [0,0,0,1,1,0,0,0,0,0,1,1,0,0,0],
           [0,0,1,0,0,0,0,0,0,0,0,0,1,0,0],
           [0,1,0,0,0,0,0,0,0,0,0,0,0,1,0],
           [0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
           [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
           [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
           [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
           [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
           [1,0,0,1,0,0,0,0,0,0,0,1,0,0,1],
           [0,1,0,0,1,0,0,0,0,0,1,0,0,1,0],
           [0,1,0,0,0,1,1,1,1,1,0,0,0,1,0],
           [0,0,1,0,0,0,0,0,0,0,0,0,1,0,0],
           [0,0,0,1,1,0,0,0,0,0,1,1,0,0,0],
           [1,0,0,0,0,1,1,1,1,1,0,0,0,0,0]]
custom10= [[0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
           [0,0,1,1,1,1,1,0,1,1,1,1,1,0,0],
           [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
           [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
           [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
           [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
           [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
           [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0],
           [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
           [0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
           [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],
           [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
           [1,0,0,0,0,0,0,1,0,0,0,0,0,0,0]]


##### Main Function #####
def main():
    # Player 1/2 Strategies:
    # - c: ConsoleStrat (enter coordinates through Console/terminal)
    # - s: ScreenStrat (click the desired square on the Screen)
    # - r: RandomStrat (any Random move)
    # - g: GreedyStrat (remove as many squares as possible (be Greedy!),
    #       but also put foe in a losing position if possible)
    # - a1: AIStrat1 (for Team 1 to make!)
    # - a2: AIStrat2 (for Team 2 to make!)
    # screenOn:
    # - True: if you want the board drawn on a screen
    # - False: if you want the board printed in the console
    # boardType: is either ...
    # - a rectangle defined by the tuple (width, height)
    #   - creates a width x height board
    #     - Eg. (5,10) is 5 long and 10 tall
    #   - 1 ≤ width ≤ 64 and 1 ≤ height
    #   - width and height can't both be 1
    # - a custom board defined by a list of lists of 0s and 1s, eg:
    #   - [[1,1,0,0], [1,1,1,0], [1,1,1,1]]
    #   - [[1,0,0,0], [1,0,1,0], [1,1,1,0], [1,1,1,1]]
    #   - [[1,1,1,1,1], [0,1,1,1,0], [0,1,1,1,0], [0,0,1,0,0], [1,1,1,1,1]]
    #   - several are listed in Custom Boards

    p1strat, p2strat = ['s', 'r'] # CHANGE ME!
    screenOn = True # CHANGE ME!
    boardType = (20,15) # CHANGE ME!
    G = Game(p1strat, p2strat, screenOn, boardType)
    G.play()
    
if __name__ == "__main__":
    main()