from state import state
import time
import random
from math import sqrt, log
from copy import copy, deepcopy
from queue import Queue


class node():
    """
	Node for MCTS. Stores the move to reach this node from its parent,
	stats for the game position, children, parent and result
	(result==none unless the position ends the game).
	"""

    def __init__(self, move=None, parent=None):
        """
        Initialize a new node with optional move and parent and initially empty
        children list and simulation stats and unspecified result.
        """
        self.move = move
        self.parent = parent
        self.visits = 0  # times this position was visited
        self.wins = 0  # average wins (wins-losses) from this position
        self.children = []
        self.result = state.PLAYERS["none"]

    def add_children(self, children):
        """
        Add a list of nodes to the children of this node.
        """
        self.children += children

    def set_result(self, result):
        """
        Set the result of this node (if we decide the node is the end of
        the game)
        """
        self.result = result

    def value(self, explore):
        """
        Calculate the UCT value of this node relative to its parent.
        Explore is for exploration vs exploitation.
        Currently explore is set to zero when choosing the best move to play so
        that the move with the highest winrate is always chossen. When searching
        explore is set to EXPLORATION constant.
        """
        # unless explore is set to zero, favor unexplored nodes
        if self.visits == 0:
            if explore == 0:
                return 0
            else:
                return float('inf')
        else:
            return self.wins / self.visits + explore * sqrt(2 * log(self.parent.visits) / self.visits)


class mctsagent():


    EXPLORE = sqrt(2)

    def __init__(self, state=state(11)):
        self.rootstate = deepcopy(state)
        self.root = node()

    def best_move(self):
        """
        Return the best move in the current tree. If the game is over, returns state.GAMEOVER
        """
        # return state.GAMEOVER if game is over.
        if self.rootstate.winner() != state.PLAYERS["none"]:
            return state.GAMEOVER

        # choose the move of the most simulated node
        max_value = max(self.root.children, key=lambda n: n.visits).visits
        max_nodes = [n for n in self.root.children if n.visits == max_value]
        best_child = random.choice(max_nodes)
        return best_child.move

    def move(self, move):
        """
        Make the passed move and update the tree.
        """
        for child in self.root.children:
            # make the child associated with the move the new root
            if move == child.move:
                child.parent = None
                self.root = child
                self.rootstate.play(child.move)
                return

        # if move is not in children, restart tree
        self.rootstate.play(move)
        self.root = node()

    def search(self, time_limit):
        """
        Search and update the search tree for a specified time in secounds.
        """
        startTime = time.perf_counter()
        # num_simulations = 0

        # do until we exceed our time limit
        while time.perf_counter() - startTime < time_limit:
            node, state = self.select_node()
            turn = state.turn()
            result = self.simulate(state)
            self.backpropogate(node, turn, result)
            # num_simulations += 1

        # print(f"Ran {str(num_simulations)} simulations in {str(time.perf_counter() - startTime)} sec")
        # print(f"Node count: {str(self.tree_size())}")

    def select_node(self):
        """
        Select a random node to simulate.
        """
        node = self.root
        state = deepcopy(self.rootstate)

        # stop if we find a leaf node
        while len(node.children) != 0:
            # descend to the maximum value node
            max_value = max(node.children, key=lambda n: n.value(self.EXPLORE)).value(self.EXPLORE)
            max_nodes = [n for n in node.children if n.value(self.EXPLORE) == max_value]
            node = random.choice(max_nodes)
            state.play(node.move)

            # if some child node has not been explored select it before expanding other children
            if node.visits == 0:
                return (node, state)

        # if the node is terminal, return the terminal node
        if self.expand(node, state):
            node = random.choice(node.children)
            state.play(node.move)
        return (node, state)

    def simulate(self, state):
        """
        Simulate a random game from the passed state and return the winner.
        """
        moves = state.moves()
        while state.winner() == state.PLAYERS["none"]:
            move = random.choice(moves)
            state.play(move)
            moves.remove(move)

        return state.winner()

    def backpropogate(self, node, turn, result):
        """
        Update the node stats on the path from the passed node to root
        """
        wins = -1 if result == turn else 1

        while node is not None:
            node.visits += 1
            node.wins += wins
            wins = -wins
            node = node.parent

    def expand(self, parent, state):
        """
        Generate the children of the passed "parent" node based on the available
        moves in the passed state and add to tree.
        """
        children = []
        if state.winner() != state.PLAYERS["none"]:
            # game is over at this node so nothing to expand
            return False

        for move in state.moves():
            child_node = node(move,parent)
            children.append(child_node)

        parent.add_children(children)
        return True

    def set_state(self, state):
        """
        Set the root state of the tree to the passed state, also restart tree
        """
        self.rootstate = deepcopy(state)
        self.root = node()

    def tree_size(self):
        """
        Count nodes in tree by BFS.
        """
        Q = Queue()
        count = 0
        Q.put(self.root)
        while not Q.empty():
            node = Q.get()
            count += 1
            for child in node.children:
                Q.put(child)
        return count