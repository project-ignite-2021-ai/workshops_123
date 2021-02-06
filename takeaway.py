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
    # First find what 'n' is (pickup_range might not be in order!)


    # Then find the remainder of 'stones' divided by n+1
    # stones = (n+1)k + m


    # If possible, take away m stones


    # Otherwise, we're losing, so return any valid stones
    return random.choice(validRange(stones, pickup_range))

def BacktrackStrat(stones, pickup_range):
    # Backtracking Strategy - works for any range!
    # Create an array/list with 'stones' elements, each index representing
    # whether you lose or win if you begin with 'index' stones
    # In this array, let 0=losing, 1=winning
    # array[0] = 0 because if you begin with 0 stones, you already lost!


    # For i=1,2,3,... stones, determine if you can take away stones
    # that puts the opponent in a losing position, then update the 
    # array


    # At the end, when i=stones, find out how many stones we need to
    # take to put the opponent in a losing position


    # Otherwise, we're losing, so return any valid stones
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