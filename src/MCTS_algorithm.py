
import time
class MCTS_agent:
    def __init__(self,root):
        if root is None:
            raise ValueError("Root node cannot be None")
        self.root = root


    def select(self):
        """
        Returns the node with the highest UCT score. 
        Stops if a terminal node is encountered.
        """
        current_node = self.root
        while not current_node.is_terminal_node():
            if current_node.is_fully_expanded():
                current_node = current_node.select_child()
            else:
                break
        return current_node
    def select_and_expand(self):
        """
        Selects the best node and expands it.
        """
        node = self.select()
        return node.expand()

    # With out parallelism number of executions is "7569"
    def get_best_move(self, simulation_time=5):
        """
        Runs MCTS for a specified time duration to find the best move.
        """
        start_time = time.time()
        searches = 0
        while time.time() - start_time < simulation_time:
            node = self.select_and_expand()
            if node:
                result, simulated_moves = node.simulate2()
                node.backpropagate(result, self.root, simulated_moves)
            
            searches+=1

        print(f'Debugging| The number of searchs performed: {searches}')
        best_child = max(self.root.children, key=lambda child: child.wins / child.visits if child.visits > 0 else 0)
        print(f'Debugging| The best move is: {best_child.move}')
        return best_child.move
    
    
