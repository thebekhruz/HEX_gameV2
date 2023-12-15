
import time
 # initialise board, colour and connection
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
            return node.is_terminal_node()
        
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
    
    

