from GhostInTheShell.Bot3.state import *
from GhostInTheShell.Bot3.node import *
from GhostInTheShell.Bot3.statistics import *


class Field:
    def __init__(self, nodes):
        self.nodes = [Node(i) for i in range(nodes)]
        self.state = State()
        self.statistics = Statistics(nodes)

    def connect(self, node_index1, node_index2, distance):
        node1 = self.nodes[node_index1]
        node2 = self.nodes[node_index2]
        node1.link(node2, distance)
        node2.link(node1, distance)

    def start_turn(self):
        [node.start_turn() for node in self.nodes]
        self.statistics.start_turn()
        self.state.start_turn()

    def end_input(self):
        [node.end_input() for node in self.nodes]
        self.statistics.end_input()

    def update_factory(self, node_id, owner, cyborgs, production, repairing):
        node_core = NodeCore(owner, owner, cyborgs, production, repairing)
        self.nodes[node_id].update(node_core)
        self.statistics.update_node(node_core)

    def update_troop(self, owner, target, cyborgs, eta):
        troop = Troop(owner, cyborgs, eta)
        self.nodes[target].incoming_troop(troop)
        self.statistics.update_troop(troop)

    def update_bomb(self, owner, source, target, eta):
        if target == 1:
            self.state.track_enemy_bomb(source, eta)
        self.nodes[target].incoming_bomb(Bomb(owner, eta))

    def choose_move(self):
        raise Exception('Not implemented yet')
