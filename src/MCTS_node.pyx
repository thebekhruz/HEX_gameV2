# cython: language_level=3
from cpython cimport array
import array

cdef class MCTS_node:
    
    cdef public int wins, visits, board_size
    cdef public object state, parent, move, player, children, untried_moves, board

    def __init__(self, state, int board_size=11, parent=None, move=None, player=None):
        self.wins = 0
        self.visits = 0
        self.state = state
        self.parent = parent
        self.move = move
        self.player = player
        self.board_size = board_size
        self.board = state
        self.children = []
        self.untried_moves = self.get_legal_moves()

    # Add your other methods here, with appropriate type definitions
