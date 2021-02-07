'''
This Nim game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Nim: The game begins with some number of piles, each with some number
of stones (most common is 3 piles, with 3, 5, and 7 stones). Each turn, a 
player takes at least 1 stone (as many as they want to and are able to)
from any 1 pile. Whoever takes the last stone is the winner.
(These are the "normal game" rules. The original, "misere" rules are
whoever takes the last stones is the LOSER)

    Eg.
       3 5 7   Player 1 takes 2 from Pile 0
    -> 1 5 7   Player 2 takes 5 from Pile 1
    -> 1 0 7   Player 1 takes 6 from Pile 2
    -> 1 0 1   Player 2 takes 1 from Pile 0
    -> 0 0 1   Player 1 takes 1 from Pile 2
    -> 0 0 0   Player 1 is the WINNER!
'''

import random

##### Game Tools #####

# Print the current piles
def printPiles(piles):
    for pileNum in range(len(piles)):
        stones = piles[pileNum]
        print("Pile %d: " % pileNum, end='')
        print(u'\u25a0 ' * stones, end=' ')
        print("(%d)" % stones)
    print()

# Check if game is over (ie. piles are empty)
def gameIsDone(piles):
    return not any(piles)

# return a list of tuples of valid moves
# (x,y): you can take y stones from Pile x
def validMoves(piles):
    valid = []
    for pileNum in range(len(piles)):
        for i in range(1,piles[pileNum]+1): #1,2,...,total stones
            valid.append((pileNum, i))
    return valid

# Given the current piles and (x,y), 
# determine if (x,y) is a valid move
def isValidMove(piles, taken):
    x,y = taken
    if x<0 or x >= len(piles) or y<=0:
        return False
    return piles[x] >= y

# Given the current piles and (x,y), 
# update the piles after taking y stones from pile x
def takeFromPiles(piles, taken):
    assert(isValidMove(piles, taken))
    x,y = taken
    piles[x] -= y


# Return the Nim sum of the list of numbers
# This is simply taking the XOR of all of them
# Eg. nim_sum(3,5,7):
#   3 = 011
#   5 = 101  -> nim_sum = 001 = 1
#   7 = 111
def nim_sum(arr):
    result = 0
    for i in arr:
        result = result ^ i
    return result

##### Player 1's and 2's Strategies #####

def RandomStrat(piles):
    # Random Strategy - return any valid move
    return random.choice(validMoves(piles))

def NimSumStrat(piles):
    # Nim Sum Strategy - return any move that would make the 
    # resulting piles have a Nim sum of 0 (ie. put the opponent
    # in a losing position).
    winning_moves = []

    # If the Nim Sum of 'piles' is already 0, we're losing, so return
    # any valid move
    if nim_sum(piles) == 0:
        return random.choice(validMoves(piles))

    # Otherwise, a winning move that makes the Nim Sum equal to 
    # 0 MUST exist.
    # To find this winning move/s, iterate through all piles and
    # run nim_sum(all piles except one). This will return the number
    # of stones that MUST be in the remaining pile to make the 
    # Nim sum equal to 0. Note that some results may not be possible.
    # Eg. piles = [3,5,7]
    #   ignore Pile 0: nim_sum(5,7) = 2; making Pile 0 = 2 is winning
    #   ignore Pile 1: nim_sum(3,7) = 4; making Pile 1 = 4 is winning
    #   ignore Pile 2: nim_sum(3,5) = 6; making Pile 2 = 6 is winning
    #   winning_moves = [(0,1), (1,1), (2,1)]
    # Eg. piles = [3,5,5]
    #   ignore Pile 0: nim_sum(5,5) = 0; making Pile 0 = 0 is winning
    #   ignore Pile 1: nim_sum(3,5) = 6; making Pile 1 = 6 is impossible
    #   ignore Pile 2: nim_sum(3,5) = 6; making Pile 2 = 6 is impossible
    #   winning_moves = [(0,3)]
    
    for pileNum in range(len(piles)):

        # take out piles[pileNum] from the piles
        piles_minus_one = piles[0:pileNum] + piles[pileNum+1:]
        final_pile = nim_sum(piles_minus_one)
        
        # append to winning_moves if winning pile is possible to reach
        if final_pile < piles[pileNum]:
            winning_moves.append((pileNum, piles[pileNum] - final_pile))

    # return any of the winning moves
    return random.choice(winning_moves)

def HumanStrat(piles):
    # Human Strategy - get user input
    while(True):
        try:
            # You can either split by commas or by spaces (or both!)
            taken = input().strip()
            test1 = taken.split(",")
            test2 = taken.split()

            if len(test1) == 2:   taken = test1
            elif len(test2) == 2: taken = test2
            else:
                print("Not a valid input")
                continue
            
            pile = int(taken[0].strip())
            stones = int(taken[1].strip())
            return (pile, stones)
        except ValueError:
            print("Not a valid input")

def Player1Strategy(piles):
    # return RandomStrat(piles)
    # return NimSumStrat(piles)
    return HumanStrat(piles)

def Player2Strategy(piles):
    # return RandomStrat(piles)
    # return NimSumStrat(piles)
    return HumanStrat(piles)



##### Main Function #####
def main():
    # piles:
    #   must be >0
    piles = [3,5,7]
    turn = 1 # player 1 is 1, player 2 is 2

    if [p for p in piles if p<=0]:
        print("Illegal initial piles")
        return

    print("Welcome to Nim!")
    print("Initial piles: ")
    printPiles(piles)
    while not gameIsDone(piles):
        # Prompt for pile and stones to take
        print("Player %d, what pile do you choose, and how many stones will you take?" % turn)
        if turn == 1:
            taken = Player1Strategy(piles)
        elif turn == 2:
            taken = Player2Strategy(piles)
        
        if not isValidMove(piles, taken):
            print("You cannot take %d stones from Pile %d." \
                % (taken[1], taken[0]))
            continue

        # Update piles, then check win condition
        takeFromPiles(piles, taken)
        print("Player %d took %d stones from Pile %d." % (turn, taken[1], taken[0]))
        print("Current piles: ")
        printPiles(piles)

        if gameIsDone(piles):
            print("Player %d is the winner!" % turn)
            break
        
        # Update turn
        if turn == 1:
            turn = 2
        elif turn == 2:
            turn = 1
    
if __name__ == "__main__":
    main()
