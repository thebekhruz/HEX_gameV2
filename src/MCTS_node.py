import math
import random
from copy import deepcopy
from Board import Board
from Colour import Colour


class MCTS_node:   
    def __init__(self, state, board_size=11, parent=None, move=None, player=None):
        # Variables for UCB selection process
        self.wins = 0           # number of wins from this node
        self.visits = 0         # number of times this node has been visited



        self.state = state      # Board state
        self.parent = parent    # A reference to the parent node
        self.move = move        # The move that led to this node
        self.player = player    # Player whos move is next 

        # Initialise the Board and the board state
        self.board_size = board_size

        self.children = []                              # List of children from this node
        # self.untried_moves = self.get_legal_moves()     # A list of moves not yet explored from this node
        self.untried_moves = set((i, j) for i in range(self.board_size) for j in range(self.board_size) if self.state[i][j] == 0)

        


    def is_terminal_node(self):
        """
        Returns:
            bool: True if the node is a terminal state, False otherwise.
        """
        board_string = self.state_to_string(self.state)
        board_instance = Board.from_string(board_string, bnf=True)
        return board_instance.has_ended()


    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def get_legal_moves(self):
        return list(self.untried_moves)
        
    def select_child(self):
        """
        Select a child with the highes UCT value.
        """
        best_score = float("-inf")
        best_child = None

        # Precomputed constants
        c = math.sqrt(2)
        parent_visits_log = math.log(self.visits) if self.visits > 0 else 0

        for child in self.children:
                if child.visits > 0:
                    ucb_score = (child.wins / child.visits) + c * math.sqrt(parent_visits_log / child.visits)
                    if ucb_score > best_score:
                        best_score = ucb_score
                        best_child = child

        return best_child

    def make_move_on_copy(self, move, state, player):
        i, j = move         # Unpack the move coordinates
        new_state = state
        new_state[i][j] = player   
        self.untried_moves.discard(move)
        return new_state

    def expand(self):
        """
            Generate new child nodes from the current node, by performing a move. 
        """

        if not self.untried_moves:
            return self
        
        move = self.untried_moves.pop()
        new_state = [row[:] for row in self.state]
        new_state[move[0]][move[1]] = self.player
        next_player = "R" if self.player == "B" else "B"
        child_node = MCTS_node(state=new_state, parent=self, move=move, player=next_player)
        self.children.append(child_node)
        return child_node


    def state_to_string(self, current_state):
        char_map = {0: '0', 'R': 'R', 'B': 'B'}  # Mapping of state to character
        return ','.join(''.join(char_map[item] for item in row) for row in current_state)
    

    def simulate2(self):
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss).
        """

        current_state = [row[:] for row in self.state]  # Efficient copying
        current_player = self.player

        moves = list(self.untried_moves)
        random.shuffle(moves)

        for move in moves:
            current_state[move[0]][move[1]] = current_player
            current_player = "R" if current_player == "B" else "B"

        board_instance = Board.from_string( self.state_to_string(current_state), bnf=True)
        board_instance.has_ended()
        return Colour.get_char(board_instance.get_winner())  # Should return win/loss

    def backpropagate(self, result, rootNode):
        """
        Backpropagate the simulation result up the tree.
        """
        self.visits += 1
        #print(str(self.wins)+":"+str(self.visits))
        if rootNode.player == result:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result, rootNode)

