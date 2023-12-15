import numpy as np
from disjoint_set import disjoint_set


class state():
    """
	Stores information representing the current state of a game of hex: board and turn.
	Functions are for playing the game and returning information about it.
	"""

    # dictionary for mapping player to ints for interal calulations
    PLAYERS = {"none": 0, "Red": 1, "Blue": 2, "red": 1, "blue": 2, "None": 0, "R": 1, "B": 2, "r": 1, "b": 2}

    # represent edges in the disjoint set for win detection
    SIDE1 = 1  # for red, top to bottom
    SIDE2 = 2  # for blue, sideways

    # move value of -1 indicates the game has ended so no move is possible
    GAMEOVER = -1

    neighbour_cells = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))

    def __init__(self, size):
        """
        Initialize the game board and give red first turn.
        Also create disjoint set structures for win checking.
        """
        self.size = size
        self.toplay = self.PLAYERS["Red"]
        self.board = np.zeros((size, size))
        self.red_set = disjoint_set()
        self.blue_set = disjoint_set()

    def play(self, cell):
        """
        Play a colour of the current turn's color in the passed cell.
        """
        if self.toplay == self.PLAYERS["Red"]:
            self.place_red(cell)
            self.toplay = self.PLAYERS["Blue"]
        elif self.toplay == self.PLAYERS["Blue"]:
            self.place_blue(cell)
            self.toplay = self.PLAYERS["Red"]

    def place_red(self, cell):
        """
        Place red
        """
        if self.board[cell] == self.PLAYERS["none"]:
            self.board[cell] = self.PLAYERS["Red"]
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a red edge connect it appropriately
        if cell[1] == 0:
            self.red_set.join(self.SIDE1, cell)
        if cell[1] == self.size - 1:
            self.red_set.join(self.SIDE2, cell)
        # join any groups connected by the new red tile
        for n in self.neighbors(cell):
            if self.board[n] == self.PLAYERS["Red"]:
                self.red_set.join(n, cell)

    def place_blue(self, cell):
        """
        Place blue
        """
        if self.board[cell] == self.PLAYERS["none"]:
            self.board[cell] = self.PLAYERS["blue"]
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a blue edge connect it appropriately
        if cell[0] == 0:
            self.blue_set.join(self.SIDE1, cell)
        if cell[0] == self.size - 1:
            self.blue_set.join(self.SIDE2, cell)
        # join any groups connected by the new blue cell
        for n in self.neighbors(cell):
            if self.board[n] == self.PLAYERS["Blue"]:
                self.blue_set.join(n, cell)

    def turn(self):
        """
        Return player with the next move.
        """
        return self.toplay

    def set_turn(self, player):
        """
        set next player
        """
        if player in self.PLAYERS.values() and player != self.PLAYERS["none"]:
            self.toplay = player
        else:
            raise ValueError('Invalid turn: ' + str(player))

    def winner(self):
        """
        Return a number corresponding to the winner,
        or none if the game is not over.
        """
        if self.red_set.connected(self.SIDE1, self.SIDE2):
            return self.PLAYERS["Red"]
        elif self.blue_set.connected(self.SIDE1, self.SIDE2):
            return self.PLAYERS["Blue"]
        else:
            return self.PLAYERS["none"]

    def neighbors(self, cell):
        """
        Return list of neighbors of the passed cell.
        """
        x = cell[0]
        y = cell[1]
        return [
            (n[0] + x, n[1] + y)
            for n in self.neighbour_cells
            if (0 <= n[0] + x < self.size) and (0 <= n[1] + y < self.size)
        ]
        # return [(n[0]+x , n[1]+y) for n in self.neighbour_cells \
        #         if (0<=n[0]+x and n[0]+x<self.size and 0<=n[1]+y and n[1]+y<self.size)]

    def moves(self):
        """
        Get a list of all moves possible on the current board.
        """
        moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[x, y] == self.PLAYERS["none"]:
                    moves.append((x, y))
        return moves

