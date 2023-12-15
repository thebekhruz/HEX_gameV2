# to run do python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" -v -p


import socket
from random import choice
from time import sleep
from state import state
from uct_agent import mctsagent
from rave_agent import rave_mctsagent



# note board here is not used internally
# instead numpy is used in the state class which maintains the game

# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Disconnecting;python3 agents/DefaultAgents/DisconnectingAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Illegal;python3 agents/DefaultAgents/IllegalMessageAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Naive;python3 agents/DefaultAgents/NaiveAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=NoConn;python3 agents/DefaultAgents/NoConnectionAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Terminaing;python3 agents/DefaultAgents/SelfTerminatingAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Timeout;python3 agents/DefaultAgents/TimeoutAgent.py" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=LongMsg;python3 agents/DefaultAgents/TooLongMessageAgent.py" -v -p



# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Alice;./agents/TestAgents/alice/alice" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Bob;./agents/TestAgents/bob/bobagent" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Jimmie;./agents/TestAgents/jimmie/Agentjimmie" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Joni;./agents/TestAgents/joni/joniagent --agent minimax --depth 2 --heuristic monte-carlo --num-playouts 500" -v -p
# python3 Hex.py "a=Minerva;python3 minerva/Communicator.py" "a=Rita;java -jar agents/TestAgents/rita/rita.jar" -v -p







class MCTS_Agent():

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, move_time=10, agent = "mcts", board_size=11):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.s.connect((self.HOST, self.PORT))
        self.board_size = board_size
        self.board = []
        self.colour = ""
        self.turn_count = 0
        self.move_time = move_time
        self.game = state(11)

        if agent == "rave":
            print("using RAVE")
            self.agent = rave_mctsagent()
        else:
            print("Using UCT")
            self.agent = mctsagent()

    def run(self):
        """Reads data until it receives an END message or the socket closes."""

        while True:
            data = self.s.recv(1024)
            if not data:
                self.close()
                break
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if (self.interpret_data(data)):
                break


    def interpret_data(self, data):
        """Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        # print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = s[2]
                self.game = state(self.board_size)
                self.agent.set_state(self.game)
                self.board = [
                    [0]*self.board_size for i in range(self.board_size)]

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                # self.print_board()  # Print the board after updating
                pass

                if s[3] == "END":
                    print()
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    # return False
                    action = [int(x) for x in s[1].split(",")]
                    # print(action)
                    self.board[action[0]][action[1]] = self.opp_colour()
                    self.play_opp(action[0], action[1])


                    self.make_move()

        return False


    def make_move(self):
        # print(self.opp_colour())
        # print("red is making a move")
        # print(self.game.turn(), "==========================================")
        # print(self.turn_count, "======================================", self.colour)
        if self.turn_count == 0:
            self.s.sendall(bytes("SWAP\n", "utf-8"))
            self.turn_count += 1
            return
        if self.colour == "R":
            # print("asdasd")
            if self.game.turn() != state.PLAYERS["Red"]:
                self.game.set_turn(state.PLAYERS["Red"])
                self.agent.set_state(self.game)

        elif self.colour == "B":
            # print("blue is making a move")
            if self.game.turn() != state.PLAYERS["Blue"]:
                self.game.set_turn(state.PLAYERS["Blue"])
                self.agent.set_state(self.game)
        else:
            return

        self.agent.search(self.move_time)
        move = self.agent.best_move()

        # print(move)

        if(move == state.GAMEOVER):
            return
        self.game.play(move)
        self.agent.move(move)
        self.turn_count += 1
        # print(chr(ord('a')+move[0])+str(move[1]+1))
        row, col = move[1], move[0]   # internal representation is a1 ,b2, c3 etc so convert
        # print(row,col)
        # print(self.game.turn(), "==========================================")

        self.s.sendall(bytes(f"{row},{col}\n", "utf-8"))
        self.board[row][col] = self.colour
        # return (True, chr(ord('a')+move[0])+str(move[1]+1))

    def play_opp(self, x, y):
        if self.opp_colour() == "R":
            self.game.set_turn(state.PLAYERS["Red"])
            self.agent.set_state(self.game)
        elif self.opp_colour() == "B":
            self.game.set_turn(state.PLAYERS["Blue"])
            self.agent.set_state(self.game)
        self.game.play((y,x)) # internally the game is maintained in col, row format, kind of like battleships a1, b2, etc.
        self.agent.set_state(self.game)
        self.board[x][y] = self.opp_colour()




    def close(self):
        self.s.close()


    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"


    def print_board(self):
        for row in self.board:
            print(' '.join(str(tile) for tile in row))
        print()





if __name__ == "__main__":
    # if you want to use the rave agent, use agent = Communicator(<time_limit> "rave")
    # change number below to change time limit
    # agent = MCTS_Agent(5)
    agent = MCTS_Agent(5, "rave")
    agent.run()