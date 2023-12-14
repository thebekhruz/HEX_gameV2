import socket
from MCTS_node import MCTS_node
from MCTS_algorithm import MCTS_agent
from copy import deepcopy
import time


"""
python3 Hex.py "a=Smart_agent;python3 src/Communicator.py" "a=Naive_agent;python3 agents/DefaultAgents/NaiveAgent.py" -v

Current number of iterations varies between 6500 to 7500 with mean of around 7000


"""


class Communicator:
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


if __name__ == "__main__":
    game = Communicator()
    game.run()


