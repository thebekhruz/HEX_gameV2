import math
import random
from copy import deepcopy
from Board import Board
from Colour import Colour

# # Import Board class: from src

# # For debugging purposes
# import time


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
        # self.board = state


        self.children = []                              # List of children from this node
        # self.untried_moves = self.get_legal_moves()     # A list of moves not yet explored from this node

        # Use a dictionary for a sparse matrix representation of the board
        self.board = { (i, j): state[i][j] for i in range(board_size) for j in range(board_size) if state[i][j] != 0 }

        # Maintain a set of legal moves
        self.untried_moves = set((i, j) for i in range(self.board_size) for j in range(self.board_size) if state[i][j] == 0)


    def update_legal_moves_after_move(self, move):
        self.untried_moves.discard(move)



    def result(self):
        """
            Returns:
              The color of the winning player ('R' or 'B'), or None if the game hasn't ended.
        """
        board_string = self.state_to_string(self.state)
        board_instance = Board.from_string(board_string, bnf=True)
        return board_instance.has_ended()


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

    # def get_legal_moves(self):
    #     legal_moves = []

    #     for i in range(self.board_size):
    #         for j in range(self.board_size):
    #             if self.state[i][j] == 0:  # 0 indicates an empty spot
    #                 legal_moves.append((i, j))

    #     return legal_moves
    # Select a child with the highes UCT value.
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
 
        return new_state
         
    def change_colour(self, player):
        pass

    def expand(self):

        """
            Function is used to generate new child nodes from the current node.
            Each child node represents a possible future state of the game resulting from a different move.
        """

        if not self.untried_moves:
            return self
        move = self.untried_moves.pop()                 
        new_state = self.make_move_on_copy(move, deepcopy(self.state), self.player)        
        next_player = "B" if self.player == "R" else "R"
        child_node = MCTS_node(state=new_state, parent=self, move=move, player=next_player)
        # child_node.update_legal_moves_after_move(move)
        self.children.append(child_node)
        return child_node


    def state_to_string(self, current_state):
        char_map = {0: '0', 'R': 'R', 'B': 'B'}  # Mapping of state to character
        return ','.join(''.join(char_map[item] for item in row) for row in current_state)
    
    def simulate(self):
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss).
        """
        current_state = self.state
        current_player = self.player
        board_instance = Board.from_string(self.state_to_string(current_state), bnf=True)

        while not board_instance.has_ended():
            possible_moves = []

            # GET LEGAL MOVES FUNCTIN
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if current_state[i][j] == 0:  
                        possible_moves.append((i, j))

            if not possible_moves:                          
                break

            move = random.choice(possible_moves)
            current_state = self.make_move_on_copy(move, current_state, current_player)
            if current_player == "B":
                current_player = "R"
            else:
                current_player = "B"
            board_string = self.state_to_string(current_state)
            board_instance = Board.from_string(board_string, bnf=True)
        #print(board_instance.print_board(bnf=False))
        #print(board_instance.get_winner())
        return Colour.get_char(board_instance.get_winner())  # Should return win/loss

    def simulate2(self):
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss).
        """
        current_state = deepcopy(self.state)
        current_player = deepcopy(self.player)
        board_instance = Board.from_string(self.state_to_string(current_state), bnf=True)
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if current_state[i][j] == 0:  # 0 indicates an empty spot
                    moves.append((i,j))
        random.shuffle(moves)

        for move in moves:
            current_state[move[0]][move[1]] = current_player 
            current_player = "R" if current_player == "B" else "B"

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
        if rootNode.player == result:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result, rootNode)
