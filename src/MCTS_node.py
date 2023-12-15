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
        self.board_size = board_size
        self.children = []      # List of children from this node
                                # Use a dictionary for a sparse matrix representation of the board
        self.board = { (i, j): state[i][j] for i in range(board_size) for j in range(board_size) if state[i][j] != 0 }
                                # Maintain a set of legal moves
        self.untried_moves = {(i, j): True for i in range(board_size) for j in range(board_size) if state[i][j] == 0}
                                # This will store 'R', 'B', or None
        self._cached_end_state = None  


    def update_legal_moves_after_move(self, move):
        self.untried_moves[move] = False



    def is_terminal_node(self):
        """
        Check if the node is a terminal state (i.e., the game has ended).
        Returns:
            bool: True if the node is a terminal state, False otherwise.
        """
        # If the cached end state is not None, then the game has ended
        if self._cached_end_state is not None:
            return True

        # Compute and cache the end state if it hasn't been done already
        board_string = self.state_to_string(self.state)
        board_instance = Board.from_string(board_string, bnf=True)
        self._cached_end_state = board_instance.has_ended()

        # Return True if the game has ended, False otherwise
        return self._cached_end_state is not None



    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def select_child(self):
        best_score = float("-inf")
        best_child = None
        c = math.sqrt(2)

        #  chose a child with the best USB score
        for child in self.children:
            ucb_score = (child.wins / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child
        return best_child


    def make_move_on_copy(self, move, state, player):
        new_state = state
        i, j = move         
        new_state[i][j] = player

        self.update_legal_moves_after_move(move)
        self._cached_end_state = None
        return new_state
         

    def expand(self):
        if all(not is_untried for is_untried in self.untried_moves.values()):
            return self

        untried_move = next(move for move, is_untried in self.untried_moves.items() if is_untried)
        new_state = self.make_move_on_copy(untried_move, deepcopy(self.state), self.player)        
        next_player = "B" if self.player == "R" else "R"
        child_node = MCTS_node(state=new_state, parent=self, move=untried_move, player=next_player)
        self.children.append(child_node)
        return child_node


    def state_to_string(self, current_state):
        char_map = {0: '0', 'R': 'R', 'B': 'B'}  # Mapping of state to character
        return ','.join(''.join(char_map[item] for item in row) for row in current_state)
    

    def simulate2(self):
        current_state = deepcopy(self.state)
        current_player = self.player
        untried_moves = [move for move, is_untried in self.untried_moves.items() if is_untried]
        random.shuffle(untried_moves)

        for move in untried_moves:
            current_state[move[0]][move[1]] = current_player 
            current_player = "R" if current_player == "B" else "B"

        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)
        return Colour.get_char(board_instance.get_winner())

    def backpropagate(self, result, rootNode):
        """
        Backpropagate the simulation result up the tree.
        """
        self.visits += 1
        if rootNode.player == result:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result, rootNode)
