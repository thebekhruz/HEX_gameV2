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

# For the agent
# Needed for the simulation so that simulation won't interfere with the actual game
from copy import deepcopy


# Import Board class: from src
from Board import Board

# For debugging purposes
import time
        
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

    def fully_expanded(self):
        return len(self.untried_moves) == 0

    def get_legal_moves(self):
        legal_moves = []

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.state[i][j] == 0:  # 0 indicates an empty spot
                    legal_moves.append((i, j))

        return legal_moves

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
        return board_instance.has_ended() is not None

    def pick_unvisited(self):
        """
        Select an unvisited child node.

        Returns:
            MCTS_node: An unvisited child node or None if all children have been visited.
        """
        for child in self.children:
            if child.visits == 0: 
                return child
        return None
    

        
    def select_child(self):
        """
        Select a child with the highes UCT value.
        """
        best_score = float("-inf")
        best_child = None

        # Iterate over the children and chose a child with the best USB score
        for child in self.children:
            c = math.sqrt(2)
            ucb_score = (child.wins / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child

        return best_child

    def make_move_on_copy(self, move):

        # print("State before move is applied:\n", self.state)
        i, j = move         # Unpack the move coordinates
        # Apply the move
        self.state[i][j] = self.player       
        # print("State after move is applied: \n", self.state)
         
        return self.state

    # def expand(self):

    #     """
    #         Function is used to generate new child nodes from the current node.
    #         Each child node represents a possible future state of the game resulting from a different move.
    #     """
    #     if self.is_terminal_node() or not self.untried_moves:
    #         # Node is either terminal or has no untried moves left
    #         return None

    #     move = self.untried_moves.pop()                 # Remove a move from untried moves
    #     new_state = self.make_move_on_copy(move)        # Apply the move to get the new state

    #     # Switch player for the next turn in Hex
    #     next_player = "B" if self.player == "R" else "R"

    #     # Create a new MCTS node for the child with the new state and the next player
    #     child_node = MCTS_node(state=new_state, parent=self, move=move, player=next_player)
    #     print(f'child_node: {child_node}')

    #     # Add the new child node to the children of the current node
    #     self.children.append(child_node)
    #     return child_node

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

        board_string = self.state_to_string(current_state)
        board_instance = Board.from_string(board_string, bnf=True)

        while board_instance.has_ended() is None:           # Continue if there's no winner yet
            # print(board_instance.has_ended())
            possible_moves = self.get_legal_moves()
            if not possible_moves:                          # No legal moves available
                break
            # print("Hello",possible_moves)
            move = random.choice(possible_moves)
            current_state = self.make_move_on_copy(move)
            current_player = "B" if current_player == "R" else "R"  # Switch player

        return board_instance.get_winner()  # Should return win/loss

    def backpropagate(self, result):
        """
        Backpropagate the simulation result up the tree.
        """
        self.visits += 1
        if self.player == result:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result)

class MCTS_agent:

    # initialise board, colour and connection
    def __init__(self,root):
        self.root = root

    def traverse(self, node):
        while node.fully_expanded():
            node = node.select_child()

        return node.pick_unvisited() or node

    def rollout_policy(self, node):
        """
        Select a child node based on the rollout policy (random selection).
        """
        return random.choice(node.children) if node.children else None

    def rollout(self, node):
        """
        Perform a rollout simulation from the given node until a terminal state is reached.
        """
        while not node.is_terminal_node():
            node = self.rollout_policy(node)
            if node is None:
                break
        return node.result()
    
    def backpropagate(self, node, result):
        """
        Backpropagate the simulation result up the tree.
        """
        while node is not None:
            node.visits += 1  # Assuming each node has 'visits' attribute
            if node.player == result:
                node.wins += 1  # Assuming each node has 'wins' attribute
            node = node.parent

    def best_child(self, node):
        """
        Select the child node with the highest number of visits.
        """
        print(f'node {node}')
        print(f'node.children {node.children}')
        best_child = max(node.children, key=lambda child: child.visits, default=None)
        print(f'Best child {best_child}')
        return best_child

    # def get_best_move(self, simulations_number):
    #     """
    #     Runs MCTS for a specified number of simulations to find the best move.
    #     Ensures that the root node has children before proceeding.
    #     """
    #     # Initial expansion of the root node if it has no children
    #     if not self.root.children:
    #         for move in self.root.untried_moves:
    #             new_state = self.root.make_move_on_copy(move)
    #             next_player = "B" if self.root.player == "R" else "R"
    #             child_node = MCTS_node(state=new_state, parent=self.root, move=move, player=next_player)
    #             self.root.children.append(child_node)

    #     for _ in range(simulations_number):
    #         node = self.select_and_expand()
    #         if node is None:
    #             continue
    #         result = node.simulate()
    #         node.backpropagate(result)

    def get_best_move(self, simulations_number):
        """
        Runs MCTS for a specified number of simulations to find the best move.
        Returns a tuple representing the best move.
        """
        # Run simulations
        for _ in range(simulations_number):
            # Traverse the tree and expand
            node = self.traverse(self.root)
            # print(f'node {node}')
            if node is None:
                # print(f'Node is none')
                continue

            # Perform a rollout simulation
            result = self.rollout(node)

            # Backpropagate the results
            self.backpropagate(node, result)

        # After all simulations, select the best child of the root
        print(f'Root: {self.root}')
        best_node = self.best_child(self.root)
        print(f'1234312 : {best_node.move}')

        
        # Return the best move as a tuple
        return best_node.move if best_node else None

        # print(f'Root.Children {self.root.children}')

        # best_child = max(self.root.children, key=lambda child: child.wins / child.visits if child.visits > 0 else 0)
        # print(f'best_child: {best_child.move}')
        # return best_child.move

class HEX_game:
    HOST = "127.0.0.1"
    PORT = 1234

    # Iteration count the higher the number the better the results 
    # Theoretifcally
    num_iterations = 100

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
                

                # print(f"Message: {message}")
                # print(f"Player: {self.player}")
                # print(f"Board: {self.board}")

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

if __name__ == "__main__":
    game = HEX_game()
    game.run()








# TODO:
# * [√] check why does get_legal_move only returns tuples which start with 0
# * the while loop in simulate does not necessarily work correctly this is because it does not return 
    # * if the game has ended but rather the colour of the winner.
<<<<<<< HEAD
# - That it for now
=======
# * The problem is thateven though i can find the termianl state i do not  guide the board where is the winning positions or how to win. 
# - That it for now
>>>>>>> 0ff6baf (test)
