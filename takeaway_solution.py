'''
This Takeaway game visualizer+algorithm was created by Brandon Wang
for the purposes of Project Ignite 2021: AI-m of the Game. Please do not 
redistribute publicly without permission.

Takeaway Game: The game starts with N stones. Each turn, a player
takes some number of stones in the range pickup_range (eg. 1,2,3).
The player who takes the last stone in the pile is the winner.
    Eg. for pickup_range = [1,2,3]
      P1   P2   P1   P2   P1
    9 -> 8 -> 7 -> 4 -> 1 -> 0; win!
'''

import pygame as pg
import random


##### Player 1's and 2's Strategies #####
# stones = current number of stones
# pickup_range = range of values you can choose from
# return number of stones to take

def validRange(stones, pickup_range):
    # return a reduced range with all of the legal stones to take
    return [taken for taken in pickup_range if taken <= stones]

def RandomStrat(stones, pickup_range):
    # Random Strategy - return any valid number of stones
    valid = validRange(stones, pickup_range)
    return random.choice(valid)

def FixedRangeStrat(stones, pickup_range):
    # Fixed Range Strategy - assume range is 1,2,..., n
    # if we're currently at (n+1)k + m, and we want to reduce it to (n+1)k,
    # we have to take away m stones
    # if we're already at (n+1)k, we're losing, so return any random number
    n = max(pickup_range)
    m = stones % (n+1)
    if m != 0 and m in pickup_range:
        return m
    return random.choice(validRange(stones, pickup_range))

def BacktrackStrat(stones, pickup_range):
    # Backtracking Strategy - works for any range!
    # work backwards from 0 stones. Determine if 1 stones is good
    # (if we can put opponent in losing position), then if 2 stones
    # is good, etc.
    # At the end, determine best move to take at 'stones'
    # if none, we're losing, so return any random number
    
    outcome = [0] * stones # 0 means losing, 1 means winning
    for i in range(1, stones): # 1, 2, ..., stones-1
        for taken in pickup_range:
            # valid move leads to opponent in losing position
            if taken <= i and outcome[i - taken] == 0:
                outcome[i] = 1
                break
    
    for taken in pickup_range:
        # choose any move that puts the opponent in a losing position
        if taken <= stones and outcome[stones - taken] == 0:
            return taken
    return random.choice(validRange(stones, pickup_range))

def HumanStrat(stones, pickup_range):
    # Human Strategy - get user input
    while(True):
        try:
            return int(input())
        except ValueError:
            print("Not a valid input")


def Player1Strategy(stones, pickup_range):
    # return RandomStrat(stones, pickup_range)
    # return FixedRangeStrat(stones, pickup_range)
    # return BacktrackStrat(stones, pickup_range)
    return HumanStrat(stones, pickup_range)

def Player2Strategy(stones, pickup_range):
    # return RandomStrat(stones, pickup_range)
    # return FixedRangeStrat(stones, pickup_range)
    # return BacktrackStrat(stones, pickup_range)
    return HumanStrat(stones, pickup_range)

##### Main Function #####
def main():
    # stones:
    #   must be >0
    # pickup_range:
    #   must be >0
    #   must not have duplicates
    #   must include 1 (to prevent certain locked states)
    stones = 29 # CHANGE ME!
    pickup_range = {1,2,3} # CHANGE ME!
    turn = 1 # player 1 is 1, player 2 is 2

    if (stones <= 0) or (1 not in pickup_range) or \
        [p for p in pickup_range if p<=0]:
        print("Illegal pickup_range or initial stones")
        return

    print("Welcome to the Pick-Up Game!")
    print("Total stones: ", stones)
    print("Pickup Range: ", pickup_range, "\n")
    while stones > 0:
        # Prompt for stones to take
        print("Player %d, how many stones will you take?" % turn)
        if turn == 1:
            taken = Player1Strategy(stones, pickup_range)
        elif turn == 2:
            taken = Player2Strategy(stones, pickup_range)
        
        valid = validRange(stones, pickup_range)
        if taken not in valid:
            print("You cannot take this number of stones. Must be in ", \
                valid)
            continue

        # Update stones, then check win condition
        stones -= taken
        print("Player %d took %d stones." % (turn, taken))
        print("Total stones: ", stones, "\n")

        if stones == 0:
            print("Player %d is the winner!" % turn)
            break
        
        # Update turn
        if turn == 1:
            turn = 2
        elif turn == 2:
            turn = 1
    
if __name__ == "__main__":
    main()