import copy
import sys
import threading
import time

from dataclasses import dataclass

from testfixtures import compare


# implement breadth first search algorithm to solve a freecell solitaire game. The problem data is read from the ifile and the solution is written to the ofile.
# The input file contains the initial state of the game and the output file contains the solution.
# The input file is in the following format:
# Each row is a stack of cards, each card is represented by a character and a number. S for spades, H for hearts, D for diamonds, C for clubs.
# The number is the rank of the card. The rank of the ace is 1. The rank of the king is 13. The rank of the queen is 12. The rank of the jack is 11.
# The rank of the 10 is 10. The rank of the 9 is 9. The rank of the 8 is 8. The rank of the 7 is 7. The rank of the 6 is 6. The rank of the 5 is 5.
# The rank of the 4 is 4. The rank of the 3 is 3. The rank of the 2 is 2.
# Initially, the first 4 stacks contain 7 cards each, and the next 4 stacks contain 6 cards each. The total number of stacks is 8.
# There are 4 free cells. Each free cell can hold one card. There are 4 foundations. Each foundation can hold 13 cards.
# Each card can be moved to any stack, if the stack is empty, or if the stack is not empty and the top card in the stack is different suit and one rank higher than the card being moved.
# Each card can be moved to the foundation if the card is the same suit and the number is one less than the top card in the foundation.
# Each card can be moved to the free cell if the free cell is empty.
# Each card can be moved to an empty foundation if the card rank is 1.

# The output file is in the following format:
# first line: the number of moves
# each line: a move
# each move is in the following format:
# freecell <card>
# meaning that the card is moved to a free cell.
# stack <card1> <card2>
# meaning that the card is moved to a stack on top of card2.
# newstack <card>
# meaning that the card is moved to an empty stack, creating a new stack.
# source <card>
# meaning that the card is moved to a foundation.

# The output file should contain the solution to the problem.
# The game ends when all the cards are in the foundations in the order 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13.

# Create the search tree.
# The search tree is a tree of all possible moves.
# The root of the tree is the initial state of the game.
# Each node of the tree is a move.


# defining the class for the card
@dataclass
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        # if other is not a card, return false
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank


# defining the class for the stack
@dataclass
class Stack:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def remove(self):
        self.cards.pop()

    def isEmpty(self):
        return len(self.cards) == 0

    def top(self):
        # if the stack is empty, return None
        if self.isEmpty():
            return None
        return self.cards[len(self.cards) - 1]

    def numberOfCards(self):
        return len(self.cards)

    def isValidMove(self, card):
        topCard = self.top()

        if topCard is not None and topCard.suit != card.suit and topCard.rank == card.rank + 1:
            return True
        else:
            return False

    def __eq__(self, other):
        for i in range(len(self.cards)):
            if not self.cards[i] == other.cards[i]:
                return False


# defining the class for the freecell
@dataclass
class FreeCell:
    def __init__(self):
        self.card = None

    def add(self, card):
        self.card = card

    def remove(self):
        self.card = None

    def isEmpty(self):
        return self.card is None

    def top(self):
        # if the freecell is empty, return None
        if self.isEmpty():
            return None
        return self.card

    def isValidMove(self, card):
        if self.isEmpty():
            return True
        else:
            return False

    def numberOfCards(self):
        if self.isEmpty():
            return 0
        else:
            return 1

    def __eq__(self, other):
        if not self.card == other.card:
            return False


# defining the class for the foundation
@dataclass
class Foundation:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def remove(self):
        self.cards.pop()

    def isEmpty(self):
        return len(self.cards) == 0

    def top(self):
        # if the foundation is empty, return None
        if self.isEmpty():
            return None
        return self.cards[len(self.cards) - 1]

    def isValidMove(self, card):
        if self.isEmpty():
            if card.rank == 1:
                return True
        else:
            topCard = self.top()
            if topCard is not None and topCard.suit == card.suit and topCard.rank == card.rank - 1:
                return True
            else:
                return False

    def numberOfCards(self):
        return len(self.cards)

    def __eq__(self, other):
        for i in range(len(self.cards)):
            if not self.cards[i] == other.cards[i]:
                return False


# defining the class for the game
@dataclass
class GameState:
    def __init__(self):
        self.freecell = [FreeCell() for _ in range(4)]
        self.stack = [Stack() for _ in range(8)]
        self.foundation = [Foundation() for _ in range(4)]

    # function to make a move
    def makeMove(self, move):
        if move.sourceType == "stack":
            self.stack[move.sourceIndex].remove()
            if move.destinationType == "stack":
                self.stack[move.destinationIndex].add(move.card)
            elif move.destinationType == "freecell":
                self.freecell[move.destinationIndex].add(move.card)
            elif move.destinationType == "foundation":
                self.foundation[move.destinationIndex].add(move.card)

        elif move.sourceType == "freecell":
            self.freecell[move.sourceIndex].remove()
            if move.destinationType == "stack":
                self.stack[move.destinationIndex].add(move.card)
            elif move.destinationType == "freecell":
                self.freecell[move.destinationIndex].add(move.card)
            elif move.destinationType == "foundation":
                self.foundation[move.destinationIndex].add(move.card)

        elif move.sourceType == "foundation":
            self.foundation[move.sourceIndex].remove()
            if move.destinationType == "stack":
                self.stack[move.destinationIndex].add(move.card)
            elif move.destinationType == "freecell":
                self.freecell[move.destinationIndex].add(move.card)
            elif move.destinationType == "foundation":
                self.foundation[move.destinationIndex].add(move.card)


# define aa function that checks if a Node is a win state
def isGoalState(node):
    # if at least one foundation is not full, return False
    for i in range(len(node.gameState.foundation)):
        # if the foundation does not have 13 cards, return False
        if node.gameState.foundation[i].numberOfCards() != 13:
            return False
        if node.gameState.foundation[i].isEmpty():
            return False
    # if all foundations are full, check if the top card of each foundation is the higher rank card
    for i in range(len(node.gameState.foundation)):
        if node.gameState.foundation[i].top().rank != 13:
            return False
    return True


# deifine a function to compare two game states and return true if they are equal
def isEqual(state1, state2):
    # for each freecell
    for i in range(4):
        # if the freecells are both empty
        if state1.freecell[i].isEmpty() and state2.freecell[i].isEmpty():
            continue
        # if the freecells are both not empty
        elif not state1.freecell[i].isEmpty() and not state2.freecell[i].isEmpty():
            # if the cards in the freecells are not equal
            if not state1.freecell[i].top() == state2.freecell[i].top():
                return False
        # if the freecells are not both empty
        else:
            return False

    # for each stack
    for i in range(8):
        # check if the lenght of the stack is equal
        if not len(state1.stack[i].cards) == len(state2.stack[i].cards):
            return False
        # check if the cards in the stack are equal
        for j in range(len(state1.stack[i].cards)):
            if not state1.stack[i].cards[j] == state2.stack[i].cards[j]:
                return False

    # for each foundation
    for i in range(4):
        # check if the lenght of the foundation is equal
        if not len(state1.foundation[i].cards) == len(state2.foundation[i].cards):
            return False
        # check if the cards in the foundation are equal
        for j in range(len(state1.foundation[i].cards)):
            if not state1.foundation[i].cards[j] == state2.foundation[i].cards[j]:
                return False

    return True


# defining the class of the tree node
class Node:
    def __init__(self, parent, move, gameState):
        self.parent = parent
        self.move = move
        self.children = []
        self.gameState = gameState
        self.depth = 0
        self.nodeNumber = None

    def __eq__(self, other):
        return isEqual(self.gameState, other.gameState)


Type = ["stack", "freecell", "foundation"]


# define the function to get the next move
def getValidMoves(gameState):
    # define the variables
    freecell = gameState.freecell
    stack = gameState.stack
    foundation = gameState.foundation
    validMoves = []

    # for each stack check if the top card can make a valid move
    for i in range(8):
        if not stack[i].isEmpty():
            # for each foundation
            # check if the move is a foundation move
            for j in range(4):
                if foundation[j].isValidMove(stack[i].top()):
                    move = Move("foundation " + str(stack[i].top().suit) + str(stack[i].top().rank),
                                stack[i].top(),
                                Type[2],
                                j,
                                Type[0],
                                i)

                    validMoves.append(move)

            # for each freecell
            # check if the move is a free cell move
            for j in range(4):
                if freecell[j].isValidMove(stack[i].top()):
                    move = Move("freecell " + str(stack[i].top().suit) + str(stack[i].top().rank),
                                stack[i].top(),
                                Type[1],
                                j,
                                Type[0],
                                i)

                    validMoves.append(move)

            # for each stack
            # check if the move is a stack move
            for j in range(8):
                if stack[j].isValidMove(stack[i].top()):
                    move = Move("stack " + str(stack[i].top().suit) + str(stack[i].top().rank) + " " + str(
                        stack[j].top().suit) + str(stack[j].top().rank),
                                stack[i].top(),
                                Type[0],
                                j,
                                Type[0],
                                i)

                    validMoves.append(move)
                # check if the move is a new stack move
                if stack[j].isEmpty():
                    move = Move("newstack " + str(stack[i].top().suit) + str(stack[i].top().rank),
                                stack[i].top(),
                                Type[0],
                                j,
                                Type[0],
                                i)

                    validMoves.append(move)

    # for each freecell check if the card in the freecell can make a valid move
    for i in range(4):
        if not freecell[i].isEmpty():
            # for each foundation
            # check if the move is a foundation move
            for j in range(4):
                if foundation[j].isValidMove(freecell[i].top()):
                    move = Move("foundation " + str(freecell[i].top().suit) + str(freecell[i].top().rank),
                                freecell[i].top(),
                                Type[2],
                                j,
                                Type[1],
                                i)

                    validMoves.append(move)

            # for each stack
            # check if the move is a stack move
            for j in range(8):
                if stack[j].isValidMove(freecell[i].top()):
                    move = Move("stack " + str(freecell[i].top().suit) + str(freecell[i].top().rank) + " " + str(
                        stack[j].top().suit) + str(stack[j].top().rank),
                                freecell[i].top(),
                                Type[0],
                                j,
                                Type[1],
                                i)

                    validMoves.append(move)
                # check if the move is a new stack move
                if stack[j].isEmpty():
                    move = Move("newstack " + str(freecell[i].top().suit) + str(freecell[i].top().rank),
                                freecell[i].top(),
                                Type[0],
                                j,
                                Type[1],
                                i)

                    validMoves.append(move)

    # check if moves are at least one
    if len(validMoves) == 0:
        return None

    # return the moves
    return validMoves


# defining the class move
class Move:
    def __init__(self, name, card, destinationType, destinationIndex, sourceType, sourceIndex):
        self.name = name
        self.card = card
        self.destinationType = destinationType
        self.destinationIndex = destinationIndex
        self.sourceType = sourceType
        self.sourceIndex = sourceIndex

    def __eq__(self, other):
        # if the other move is not a move
        if not isinstance(other, Move):
            return False
        return self.name == other.name


# define the function used to get the next state
def getNextState(currentGameState, move):
    # create a copy of the current game state
    nextGameState = copy.deepcopy(currentGameState)

    # make the move in the next game state
    nextGameState.makeMove(move)

    # compare the next game state with the current game state
    if isEqual(nextGameState, currentGameState):
        print("The states are equal")

    # return the next game state
    return nextGameState


# define the function used to find new nodes and add them to the frontier
def findNewNodes(node):
    # get the valid moves
    validMoves = getValidMoves(node.gameState)

    # define the children nodes
    childrenNodes = []

    # if there are no valid moves
    if validMoves is None:
        return None

    foundFoundationMoves = False

    # for each valid move
    for move in validMoves:
        # check if at least one is a foundation move
        if move.destinationType == Type[2]:
            # if the move is a foundation move
            # create a new node
            childNode = Node(node, move, getNextState(node.gameState, move))
            # set newNode depth
            childNode.depth = node.depth + 1
            # add the new node to the children nodes
            childrenNodes.append(childNode)
            # set the flag to true
            foundFoundationMoves = True
    if foundFoundationMoves:
        return childrenNodes

    # for each valid move
    for move in validMoves:
        # find the next state
        nextState = getNextState(node.gameState, move)

        # create a new child node
        childNode = Node(node, move, nextState)
        childNode.depth = node.depth + 1

        # if the child node is not same with other child nodes
        if not sameChild(childNode, childrenNodes):
            # add the child node to the children nodes
            childrenNodes.append(childNode)

    # return the children nodes
    return childrenNodes


# define a function used to check if a child is the same as other children
def sameChild(child, children):
    # for each child
    for otherChild in children:
        # if the child is the same as the other child
        if child.move == otherChild.move:
            return True
    # return false
    return False


# define the Breadth First Search function that is used to find the solution
def BFS(rootNode):
    # define visited states
    visitedNodes = []
    # define the queue
    queue = []

    # define garbage nodes
    garbageNodes = []

    # define moves already made
    movesMade = []

    # add the root state to the queue
    queue.append(rootNode)

    # add the root node to the visited nodes
    visitedNodes.append(rootNode)

    # define flag for the loop
    solutionFound = False

    currentNodeNumber = 0

    # set an execution time meter
    startTime = time.time()

    maxExecutionTime = 30.0

    # while the queue is not empty or the goal state is not found
    while len(queue) > 0 or (not solutionFound):

        # get the first state in the queue
        if len(queue) > 0:
            currentNode = queue.pop(0)
            currentNodeNumber += 1
            currentNodeDepth = currentNode.depth
            movesMade.append(currentNode.move)
        else:
            return visitedNodes

        endTime = time.time()
        executionTime = endTime - startTime

        # print current execution time

        # print("Current execution time: " + str(round(executionTime / 60, 1)) + " minutes. "
        #       + "Current depth: " + str(currentNode.depth)
        #       + " Queue length: " + str(len(queue)), end="\n")

        # if the execution time is greater than the maximum execution time
        if round(executionTime / 60, 1) > maxExecutionTime:
            # return the visited nodes
            return movesMade

        # if the current node has the goal state
        if isGoalState(currentNode):
            # set the flag to true
            solutionFound = True
            # print("Goal state found")
            print("Goal state found at depth", currentNode.depth)
            # find the execution time
            endTime = time.time()
            executionTime = endTime - startTime

            # convert the execution time to seconds

            # print execution time in seconds
            print("Execution time: " + str(round(executionTime / 60, 1)) + " minutes")

            # return the visited nodes
            return movesMade

        else:
            # find the children nodes
            childrenNodes = findNewNodes(currentNode)

            # if children nodes are not none
            if childrenNodes is not None:
                # for each child node
                for childNode in childrenNodes:
                    # if the child node is not visited
                    if not isVisited(visitedNodes, childNode):
                        # add the child node to the queue
                        queue.append(childNode)
                        # add the children to the parent node
                        currentNode.children.append(childNode)

                        lastNodeDepth = childNode.depth

                        # add the child node to the visited nodes
                        visitedNodes.append(childNode)

    # find the execution time
    endTime = time.time()
    executionTime = endTime - startTime

    # convert the execution time to seconds
    executionTime = executionTime * 1000
    # print execution time in seconds
    print("Execution time: " + str(executionTime) + " seconds\n")
    print("No solution found !!!\n")

    # return the visited nodes
    return movesMade


# define a function that checks if a game state is equal to another game state
def isEqualState2(state1, state2):
    # find the top cards in the stacks in state 1
    topCardsInStacksState1 = []
    for stack in state1.stack:
        topCardsInStacksState1.append(stack.top())

    # find the top cards in the stacks in state 2
    topCardsInStacksState2 = []
    for stack in state2.stack:
        topCardsInStacksState2.append(stack.top())

    # for each top stack card in state 1
    for topCard in topCardsInStacksState1:
        # if the top stack card is not in state 2
        if topCard not in topCardsInStacksState2:
            # return false
            return False

    # for each top stack card in state 2
    for topCard in topCardsInStacksState2:
        # if the top stack card is not in state 1
        if topCard not in topCardsInStacksState1:
            # return false
            return False

    # find the top cards in the foundations in state 1
    topCardsInFoundationsState1 = []
    for foundation in state1.foundation:
        topCardsInFoundationsState1.append(foundation.top())

    # find the top cards in the foundations in state 2
    topCardsInFoundationsState2 = []
    for foundation in state2.foundation:
        topCardsInFoundationsState2.append(foundation.top())

    # for each top foundation card in state 1
    for topCard in topCardsInFoundationsState1:
        # if the top foundation card is not in state 2
        if topCard not in topCardsInFoundationsState2:
            # return false
            return False

    # for each top foundation card in state 2
    for topCard in topCardsInFoundationsState2:
        # if the top foundation card is not in state 1
        if topCard not in topCardsInFoundationsState1:
            # return false
            return False

    # find the cards in freecells in state 1
    cardsInFreecellsState1 = []
    for freecell in state1.freecell:
        cardsInFreecellsState1.append(freecell.top())

    # find the cards in freecells in state 2
    cardsInFreecellsState2 = []
    for freecell in state2.freecell:
        cardsInFreecellsState2.append(freecell.top())

    # for each card in freecells in state 1
    for card in cardsInFreecellsState1:
        # if the card is not in freecells in state 2
        if card not in cardsInFreecellsState2:
            # return false
            return False

    # for each card in freecells in state 2
    for card in cardsInFreecellsState2:
        # if the card is not in freecells in state 1
        if card not in cardsInFreecellsState1:
            # return false
            return False

    return True
    # find which cards are in


# define a function to check if a same node is already in queue
def sameInQueue(queue, node):
    # for each node in the queue
    for n in queue:
        # if the node is the same
        if n == node:
            # return true
            return True
    # return false
    return False


# check if visited states contains the game state
def isVisited(visitedNodes, currentNode):
    # for each visited node
    for visitedNode in visitedNodes:
        # if the visited node has the same game state
        if isEqual(visitedNode.gameState, currentNode.gameState) or isEqualState2(visitedNode.gameState, currentNode.gameState):
            # return true
            return True

    # return false
    return False


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Usage: python Solver.py <Algorithm> <inputFileName> <outputFilename>")
        sys.exit(-1)
    else:
        ifile = [line.replace("\n", "").split() for line in open(sys.argv[2], 'r', encoding='utf-8')]
        print(ifile, "\n")
        # ofile = sys.argv[len(sys.argv) - 0]

        # Create the game.
        gameState = GameState()

        # Populate the game stacks.
        for i in range(len(ifile)):
            for j in range(len(ifile[i])):
                # create a new card
                card = Card(ifile[i][j][0], int(ifile[i][j][1:]))
                # print(card)
                # print(card.suit, card.rank, "\n")

                # initially populate the stacks with the cards
                if gameState.stack[0].numberOfCards() < 7:
                    gameState.stack[0].add(card)
                elif gameState.stack[1].numberOfCards() < 7:
                    gameState.stack[1].add(card)
                elif gameState.stack[2].numberOfCards() < 7:
                    gameState.stack[2].add(card)
                elif gameState.stack[3].numberOfCards() < 7:
                    gameState.stack[3].add(card)
                elif gameState.stack[4].numberOfCards() < 6:
                    gameState.stack[4].add(card)
                elif gameState.stack[5].numberOfCards() < 6:
                    gameState.stack[5].add(card)
                elif gameState.stack[6].numberOfCards() < 6:
                    gameState.stack[6].add(card)
                elif gameState.stack[7].numberOfCards() < 6:
                    gameState.stack[7].add(card)
                else:
                    print("Error: All stacks are full !! Try a different input file.\n")

        # create the root node of the search tree
        rootNode = Node(None, None, gameState)
        rootNode.depth = 0

        # run the algorithm
        if sys.argv[1] == "BFS" or sys.argv[1] == "bfs" or sys.argv[1] == "B" or sys.argv[1] == "b":
            movesMade = BFS(rootNode)
            # print(visitedNodes) from number 1 to end
            # if there are more than one visited nodes
            # if len(movesMade) > 1:
            #     for move in movesMade[1:]:
            #         # if move name is not none
            #         if move.name is not None:
            #             print(move.name)
            # else:
            #     print("No solution")

            # write the moves to the output file
            with open(sys.argv[3], 'w', encoding='utf-8') as f:
                # if movesMade is not empty
                if movesMade is not None:
                    # for each move in movesMade
                    for move in movesMade:
                        # if move name is not none
                        if move is not None:
                            # write the move name to the output file
                            f.write(move.name + "\n")

                else:
                    # write No solution to the output file
                    f.write("No solution")