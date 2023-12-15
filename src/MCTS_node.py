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
        legal_moves = []

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.state[i][j] == 0:  # 0 indicates an empty spot
                    legal_moves.append((i, j))

        return legal_moves
        
    def select_child(self):
        """
        Select a child with the highes UCT value.
        """
        best_score = float("-inf")
        best_child = None

        for child in self.children:
            c = math.sqrt(2)
            ucb_score = (child.wins / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child

        return best_child

    def make_move_on_copy(self, move, state, player):
        i, j = move         # Unpack the move coordinates
        new_state = state
        new_state[i][j] = player       
        return new_state

    def expand(self):

        """
            Function is used to generate new child nodes from the current node.
            Each child node represents a possible future state of the game resulting from a different move.
        """
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
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss).
        """
        current_state = deepcopy(self.state)
        current_player = deepcopy(self.player)

        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if current_state[i][j] == 0:  # 0 indicates an empty spot
                    moves.append((i,j))
        random.shuffle(moves)
        for move in moves:
            current_state[move[0]][move[1]] = current_player 
            if current_player == "B":
                current_player = "R"
            else:
                current_player = "B"
        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)
        #print(board_instance.print_board(bnf=False))
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

