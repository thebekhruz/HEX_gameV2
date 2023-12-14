from Smart_Agent import MCTS_node, MCTS_agent

def test_mcts_node_initialization():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert node.wins == 0
    assert node.visits == 0
    assert node.state == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert node.parent is None
    assert node.move is None
    assert node.player is None
    assert node.children == []
    assert node.untried_moves == []

def test_mcts_node_get_legal_moves():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert node.get_legal_moves() == [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]



def test_mcts_node_initialization():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert node.wins == 0
    assert node.visits == 0
    assert node.state == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert node.parent is None
    assert node.move is None
    assert node.player is None
    assert node.children == []
    assert node.untried_moves == []

def test_mcts_node_get_legal_moves():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert node.get_legal_moves() == [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

def test_mcts_node_select_child():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    child_node1 = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 1]])
    child_node2 = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 1, 0]])
    node.children = [child_node1, child_node2]
    best_child = node.select_child()
    assert best_child == child_node2

def test_mcts_node_expand():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    child_node = node.expand()
    assert child_node in node.children
    assert child_node.parent == node
    assert child_node.move in node.untried_moves

def test_mcts_node_simulate():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    result = node.simulate()
    assert result == "draw"

def test_mcts_node_backpropagate():
    node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    child_node = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 1]])
    node.children = [child_node]
    node.backpropagate("win")
    assert node.wins == 1
    assert child_node.parent == node
    assert child_node.wins == 1

def test_mcts_agent_initialization():
    agent = MCTS_agent(root=MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]))
    assert agent.root.state == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

def test_mcts_agent_select():
    agent = MCTS_agent(root=MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]))
    child_node1 = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 0, 1]])
    child_node2 = MCTS_node(state=[[0, 0, 0], [0, 0, 0], [0, 1, 0]])
    agent.root.children = [child_node1, child_node2]
    best_child = agent.select()
    assert best_child == child_node2

