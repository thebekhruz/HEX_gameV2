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
        self.untried_moves = set((i, j) for i in range(self.board_size) for j in range(self.board_size) if state[i][j] == 0)
                                # This will store 'R', 'B', or None
        self._cached_end_state = None 

        self.rave_wins = {}     # RAVE wins for each move
        self.rave_visits = {}   # RAVE visits for each move
        self.simulated_moves = []


    def update_legal_moves_after_move(self, move):
        self.untried_moves.discard(move)



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
        # c = math.sqrt(3)
        c = 4



        for child in self.children:
            ucb_score = (child.wins / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits) if child.visits > 0 else float("inf")
            rave_score = self.rave_wins.get(child.move, 0) / self.rave_visits.get(child.move, 1) 
            beta = math.sqrt(self.rave_visits.get(child.move, 0) / (3 * self.visits + self.rave_visits.get(child.move, 0)))
            combined_score = beta * rave_score + (1 - beta) * ucb_score
            flag+=1
            if combined_score > best_score:
                best_score = combined_score
                best_child = child
        return best_child


    def make_move_on_copy(self, move, state, player):
        new_state = state
        i, j = move         
        new_state[i][j] = player

        self.update_legal_moves_after_move(move)
        self._cached_end_state = None
        return new_state
         
    def change_colour(self, player):
        pass

    def expand(self):
        """
            Generate new child nodes from the current node, by performing a move. 
        """
        if not self.untried_moves:
            return self
        move = self.untried_moves.pop()                 
        new_state = self.make_move_on_copy(move, deepcopy(self.state), self.player)        
        next_player = "B" if self.player == "R" else "R"
        child_node = MCTS_node(state=new_state, parent=self, move=move, player=next_player)
        self.children.append(child_node)
        return child_node


    def state_to_string(self, current_state):
        char_map = {0: '0', 'R': 'R', 'B': 'B'}  # Mapping of state to character
        return ','.join(''.join(char_map[item] for item in row) for row in current_state)
    

    def simulate2(self):
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss) and the list of moves made.
        """
        current_state = deepcopy(self.state)
        current_player = self.player
        simulated_moves = []  # Local list for tracking moves
        moves = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if current_state[i][j] == 0]
        random.shuffle(moves)

        for move in moves:
            current_state[move[0]][move[1]] = current_player
            simulated_moves.append(move)  # Store the move
            current_player = "R" if current_player == "B" else "B"

        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)
        board_instance.has_ended()
        return Colour.get_char(board_instance.get_winner()), simulated_moves

    def backpropagate(self, result, rootNode, simulated_moves):
        """
        Backpropagate the simulation result up the tree.
        """
        self.visits += 1
        if rootNode.player == result:
            self.wins += 1

        # Update RAVE statistics
        current_node = self
        while current_node is not None:
            for move in simulated_moves:
                if move not in current_node.rave_wins:
                    current_node.rave_wins[move] = 0
                    current_node.rave_visits[move] = 0
                current_node.rave_visits[move] += 1
                if result == rootNode.player:
                    current_node.rave_wins[move] += 1
            current_node = current_node.parent

