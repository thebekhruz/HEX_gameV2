# To run use:
# python3 Hex.py "a=Group888;python3 src/Smart_Agent.py"
# python3 Hex.py "a=Smart_agent;python3 src/Smart_Agent.py" "a=Naive_agent;python3 agents/DefaultAgents/NaiveAgent.py" -v -p

# For connection
import socket

# For UST
import math

# For Simulation step:
import random
from random import choice
from random import shuffle

# For the agent
# Needed for the simulation so that simulation won't interfere with the actual game
from copy import deepcopy

# Import Board class: from src
from Board import Board
from Colour import Colour

# For debugging purposes
import time

class MCTS_agent:

    # initialise board, colour and connection
    def __init__(self,root):
        if root is None:
            raise ValueError("Root node cannot be None")
        self.root = root
        # self.root = root


    # The first step in MCTS -! SELECTION !-
    # Select is a helper function, the function used in select_and_expand later.
    def select(self):
        """
        Returns the node with the highest UCT score. 
        Stops if a terminal node is encountered.
        """
        current_node = self.root
        while current_node is not None and not current_node.is_terminal_node():
            if current_node.is_fully_expanded():
                current_node = current_node.select_child()
                if current_node is None:
                    raise RuntimeError("Current node is None during selection")
            else:
                # If the node is not fully expanded, we should stop and return this node
                # for expansion, as per the standard MCTS procedure.
                break
        return current_node
    def select_and_expand(self):
        """
        Selects the best node and expands it.
        """

        node = self.select()
        return node.expand()

    def simulate(self):
        """
        Runs a simulation of the MCTS tree from the current node.

        Returns:
            The result of the simulation (win/loss/draw).
        """
        node = self.select_and_expand()
        if node.is_terminal_node():
            return node.result()
        
        return node.simulate()
    
    def get_best_move(self, simulations_number):
        """
        Runs MCTS for a specified number of simulations to find the best move.
        """
        searches = 0
        start_time = time.time()
        results= {"red": 0, "blue":0}
        while time.time() < start_time + 5:
            searches+=1
        #for _ in range(100):
            node = self.select_and_expand()
            result = node.simulate2()
            if result == "R":
                results["red"]+=1
            else:
                results["blue"]+=1
            node.backpropagate(result,self.root)
        print(searches)
        print(results)
        best_child = max(self.root.children, key=lambda child: child.wins / child.visits if child.visits > 0 else 0)
        #for child in self.root.children:
        #   print("child visits vs wins: "+str(child.visits)+":"+str(child.wins))
        print("Best child visits vs wins: "+str(best_child.visits)+":"+str(best_child.wins))
        print(f'best_child: {best_child.move}')
        return best_child.move
    
    


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



    def result(self):
        """
            Returns:
              The color of the winning player ('R' or 'B'), or None if the game hasn't ended.

        """
        board_string = self.state_to_string(self.state)
        board_instance = Board.from_string(board_string, bnf=True)
        game_result = board_instance.has_ended()

        return game_result


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
    
    def simulate(self):
        """
        Simulate a random play-out from this node's state.
        Returns: the result of the simulation (win/loss).
        """
        current_state = deepcopy(self.state)
        current_player = deepcopy(self.player)

        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)

        while not board_instance.has_ended():           # Continue if there's no winner yet
            # print(board_instance.has_ended())

            possible_moves = []

            for i in range(self.board_size):
                for j in range(self.board_size):
                    if current_state[i][j] == 0:  # 0 indicates an empty spot
                        possible_moves.append((i, j))

            #possible_moves = self.get_legal_moves()
            if not possible_moves:                          # No legal moves available
                break
            # print("Hello",possible_moves)
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




class HEX_game:
    HOST = "127.0.0.1"
    PORT = 1234

    # Iteration count the higher the number the better the results 
    # Theoretifcally
    num_iterations = 1000

    def __init__(self, board_size=11):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
        self.board_size = board_size
        self.board = [[0] * board_size for _ in range(board_size)]
        self.turn_count = 0
        self.player = None
        self.root = None


    def create_game_state(self):
        return deepcopy(self.board)

    def run(self):
        while True:
            data = self.s.recv(1024)
            if not data:
                break
            if self.interpret_data(data):
                break

    def interpret_data(self, data):
        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]


        for message in messages:
            # parts = message.split(";")
            if message[0] == "START":

                self.board_size = int(message[1])
                self.player = message[2]  
                self.board = [[0] * self.board_size for _ in range(self.board_size)]
                self.root = MCTS_node(state=self.create_game_state(), player=self.player)
                

                print(f"Message: {message}")
                print(f"Player: {self.player}")
                print(f"Board: {self.board}")

                time.sleep(1)

                if self.player == "R":
                    self.make_move()

            elif message[0] == "END":
                return True

            elif message[0] == "CHANGE":
                # TODO:
                # self.print_board()
                # Should do something here

                if message[3] == "END":
                    return True

                elif message[1] == "SWAP":
                    # print(f"Message: {message}")
                    # print(f"Player: {self.player}")
                    # print(f"Board: {self.board}")
                    # print('\n######################\n')
                    self.handle_swap()
                    if message[3] == self.player:
                        self.make_move()
                    # print(f"Message: {message}")
                    # print(f"Player: {self.player}")
                    # print(f"Board: {self.board}")

                elif message[3] == self.player:
                    action = [int(x) for x in message[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_player()
                    self.make_move()

        return False
    def make_move(self):
        root_state = self.create_game_state()
        root_node = MCTS_node(state=root_state, player=self.player)
        mcts = MCTS_agent(root_node)
        best_move = mcts.get_best_move(self.num_iterations)

        self.s.sendall(bytes(f"{best_move[0]},{best_move[1]}\n", "utf-8"))
        self.board[best_move[0]][best_move[1]] = self.player
        self.turn_count += 1

    def opp_player(self):
        return "B" if self.player == "R" else "R"
    

    def handle_swap(self):
        """
        Handles the 'SWAP' action by updating the MCTS tree.
        """
        # Switch the player's color
        self.player = self.opp_player()
        # print(f'Player Colour after the Swap {self.player}')

        # Update the root node of the MCTS tree
        new_root_state = deepcopy(self.board)  # Assuming self.board reflects the current board state
        self.root = MCTS_node(state=new_root_state, player=self.player)
        return
    
    def print_board(self):
        for row in self.board:
            print(' '.join(str(tile) for tile in row))
        print() 





# TODO:
# * [√] check why does get_legal_move only returns tuples which start with 0
# * the while loop in simulate does not necessarily work correctly this is because it does not return 
    # * if the game has ended but rather the colour of the winner.
# - That it for now