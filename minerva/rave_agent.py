from state import state
import time
import random
from math import sqrt, log
import math
from copy import copy, deepcopy
from queue import Queue


class rave_node():
    def _init_(self, move=None, parent=None):
        """
        Initialize a new node with optional move and parent and initially empty
        children list and simulation statistics and unspecified outcome.
        """
        self.move = move
        self.parent = parent
        self.visits = 0  # times this position was visited
        self.wins = 0  # average wins (wins-losses) from this position
        self.wins_RAVE = 0  # times this move has been critical in a simulation
        self.visits_RAVE = 0  # times this move has appeared in a simulation
        self.children = {}
        self.outcome = state.PLAYERS["none"]

    def add_children(self, children):
        for child in children:
            self.children[child.move] = child

    def set_outcome(self, outcome):
        """
        Set the outcome of this node (i.e. if we decide the node is the end of
        the game)
        """
        self.outcome = outcome

    def value(self, explore, crit):
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to zero when choosing the best move to play so
        that the move with the highest winrate is always chossen. When searching
        explore is set to EXPLORE specified above.
        """
        # unless explore is set to zero, favor unexplored nodes
        if self.visits == 0:
            if explore == 0:
                return 0
            else:
                return float('inf')
        else:
            # rave calcuation:
            alpha = max(0, (crit - self.visits) / crit)
            return self.wins * (1 - alpha) / self.visits + self.wins_RAVE * alpha / self.visits_RAVE


class rave_mctsagent():


    RAVE_CONSTANT = 250
    EXPLORE = 1.47

    def _init_(self, state=state(11)):
        self.rootstate = deepcopy(state)
        self.root = rave_node()
        self.time_budget = 300
        self.time_spent = 0
        self.moves_played = 0
        self.total_expected_moves = 60




    def calculate_time_budget(self):
        # More time for initial moves, less for later moves
        remaining_moves = self.total_expected_moves - self.moves_played
        remaining_time = self.time_budget - self.time_spent
        if remaining_moves > 45:
            return 10
        else:
            return remaining_time/remaining_moves

        # if remaining_moves > 0:
        #     # Weighted time allocation (e.g., exponential decrease)
        #     weight = math.exp((-self.moves_played / self.total_expected_moves)+0.5)
        #     return weight * remaining_time / remaining_moves
        # else:
        #     return 0



    def best_move(self):
        """
        Return the best move in the current tree. If the game is over, returns state.GAMEOVER
        """
        if self.rootstate.winner() != state.PLAYERS["none"]:
            return state.GAMEOVER

        # choose the move of the most simulated node
        max_value = max(self.root.children.values(), key=lambda n: n.visits).visits
        max_nodes = [n for n in self.root.children.values() if n.visits == max_value]
        bestchild = random.choice(max_nodes)
        return bestchild.move

    def move(self, move):
        """
        Make the passed move and update the tree.
        """
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.rootstate.play(child.move)
            return

        # if move is not in children, restart
        self.rootstate.play(move)
        self.root = rave_node()

    def search(self, time_budget):
        """
        Search and update the search tree for a specified time in secounds.
        """
        startTime = time.perf_counter()
        time_budget = self.calculate_time_budget()
        num_simulations = 0

        # do until we exceed our time budget
        while time.perf_counter() - startTime <time_budget:
            node, state = self.select_node()
            turn = state.turn()
            outcome, blue_rave_pts, red_rave_pts = self.simulate(state)
            self.backpropogate(node, turn, outcome, blue_rave_pts, red_rave_pts)
            num_simulations += 1

        self.time_spent += time.perf_counter() - startTime
        self.moves_played +=1

        print(f"Ran {str(num_simulations)} simulations in {str(time.perf_counter() - startTime)} sec")
        print(f"Node count: {str(self.tree_size())}")

    def select_node(self):
        """
        Select a random node to simulate.
        """
        node = self.root
        state = deepcopy(self.rootstate)

        # stop if we find a leaf node
        while len(node.children) != 0:
            # descend to the maximum value node
            max_value = max(node.children.values(), key=lambda n: n.value(self.EXPLORE, self.RAVE_CONSTANT)).value(
                self.EXPLORE, self.RAVE_CONSTANT)
            max_nodes = [n for n in node.children.values() if n.value(self.EXPLORE, self.RAVE_CONSTANT) == max_value]
            node = random.choice(max_nodes)
            state.play(node.move)

            # if some child node has not been explored select it before expanding other children
            if node.visits == 0:
                return (node, state)

        # if we reach a leaf node generate its children and return one of them
        # if the node is terminal, just return the terminal node
        if self.expand(node, state):
            node = random.choice(list(node.children.values()))
            state.play(node.move)
        return (node, state)

    def simulate(self, state):
        """
        Simulate a random game except play all known critical
        cells first, return the winner and record critical cells at the end.
        """
        moves = state.moves()
        while state.winner() == state.PLAYERS["none"]:
            move = random.choice(moves)
            state.play(move)
            moves.remove(move)

        blue_rave_pts = []
        red_rave_pts = []

        for x in range(state.size):
            for y in range(state.size):
                if state.board[(x, y)] == state.PLAYERS["blue"]:
                    blue_rave_pts.append((x, y))
                elif state.board[(x, y)] == state.PLAYERS["red"]:
                    red_rave_pts.append((x, y))

        return state.winner(), blue_rave_pts, red_rave_pts

    def backpropogate(self, node, turn, outcome, blue_rave_pts, red_rave_pts):
        """
        Update the node stats on the path from the passed node to root
        """
        # note that wins is calculated for player who just played
        # at the node and not the next player to play
        wins = -1 if outcome == turn else 1

        while node is not None:
            if turn == state.PLAYERS["red"]:
                for point in red_rave_pts:
                    if point in node.children:
                        node.children[point].wins_RAVE += -wins
                        node.children[point].visits_RAVE += 1
            else:
                for point in blue_rave_pts:
                    if point in node.children:
                        node.children[point].wins_RAVE += -wins
                        node.children[point].visits_RAVE += 1

            node.visits += 1
            node.visits += wins
            if turn == state.PLAYERS["blue"]:
                turn = state.PLAYERS["red"]
            else:
                turn = state.PLAYERS["blue"]
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
            children.append(rave_node(move, parent))

        parent.add_children(children)
        return True

    def set_state(self, state):
        """
        Set the root state of the tree to the passed state, also restart tree
        """
        self.rootstate = deepcopy(state)
        self.root = rave_node()

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
            for child in node.children.values():
                Q.put(child)
        return count