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
        # self.board = [[0]*self.board_size for i in range(self.board_size)]
        self.board = state


        self.children = []                              # List of children from this node
        self.untried_moves = self.get_legal_moves()     # A list of moves not yet explored from this node

        self._cached_end_state = None  


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

    def get_legal_moves(self):
        legal_moves = []

        for i in range(self.board_size):
            for j in range(self.board_size):
                # print(f"Checking tile at ({i}, {j}): {self.state[i][j]}")
                if self.state[i][j] == 0:  # 0 indicates an empty spot
                    legal_moves.append((i, j))

        # print(f"Legal moves: {legal_moves}")
        return legal_moves
        
    def select_child(self):
        """
        Select a child with the highes UCT value.
        """
        best_score = float("-inf")
        best_child = None

        # Iterate over the children and chose a child with the best USB score
        for child in self.children:
            # C constant
            c = math.sqrt(2)
            # Calculate the UCB score
            ucb_score = (child.wins / child.visits) + c * math.sqrt(
                math.log(self.visits) / child.visits
            )
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child

        return best_child

    def make_move_on_copy(self, move, state, player):

        # print("State before move is applied:\n", self.state)
        i, j = move         # Unpack the move coordinates
        new_state = state
        # Apply the move
        new_state[i][j] = player       
        # print("State after move is applied: \n", self.state)
        self._cached_end_state = None
        return new_state

    def expand(self):
        # Generate new child nodes from the current node, by performing a move. 


        if not self.untried_moves:
            return self
        move = self.untried_moves.pop()                 # Remove a move from untried moves
        new_state = self.make_move_on_copy(move, deepcopy(self.state), self.player)        # Apply the move to get the new state

        # Switch player for the next turn in Hex
        next_player = "B" if self.player == "R" else "R"

        # Create a new MCTS node for the child with the new state and the next player
        child_node = MCTS_node(state=new_state, parent=self, move=move, player=next_player)

        # Add the new child node to the children of the current node
        self.children.append(child_node)
        return child_node

    def state_to_string(self, current_state):
        char_map = {0: '0', 'R': 'R', 'B': 'B'}  # Mapping of state to character
        return ','.join(''.join(char_map[item] for item in row) for row in current_state)
    

    def simulate2(self):

        current_state = deepcopy(self.state)
        current_player = self.player

        board_instance = Board.from_string(self.state_to_string(current_state), bnf=True)
        moves = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if current_state[i][j] == 0]
        random.shuffle(moves)
        for move in moves:
            current_state[move[0]][move[1]] = current_player 
            current_player = "R" if current_player == "B" else "B"


        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)
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

