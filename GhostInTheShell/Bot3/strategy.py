from GhostInTheShell.Bot3.constants import *
from GhostInTheShell.Bot3.events import *
from GhostInTheShell.Bot3.turn import *

# Strategy constants
INNER_NODE_COST = 2
BORDER_NODE_COST = 1


class Strategy:
    def __init__(self, field):
        self.field = field
        self.my_nodes = []
        self.neutral_nodes = []
        self.neutral_my_border_nodes = []
        self.enemy_nodes = []
        self.enemy_my_border_nodes = []
        self.my_inner_nodes = []
        self.my_enemy_border_nodes = []
        self.my_neutral_border_nodes = []

        self.moves = TurnPlan()

    def prepare_turn(self):
        for node in self.field.nodes:
            if node.core.owner == MY:
                self.my_nodes.append(node)
                if node.is_border and node.is_enemy_border:
                    self.my_enemy_border_nodes.append(node)
                elif node.is_border:
                    self.my_neutral_border_nodes.append(node)
                else:
                    node.calculate_max_leave()
                    self.my_inner_nodes.append(node)
            if node.core.owner == ENEMY:
                self.my_nodes.append(node)
                if node.is_border and node.is_enemy_border:
                    node.calculate_max_leave()
                    self.enemy_my_border_nodes.append(node)
            self.neutral_nodes.append(node)
            if node.is_border and MY in node.bordering:
                self.neutral_my_border_nodes.append(node)

    def build_turn(self):
        self.build_inner_turns()
        self.build_neutral_border_turns()

    def build_neutral_border_turns(self):
        pass

    def build_inner_turns(self):
        self.my_inner_nodes.sort(key=lambda x: x.max_leave, reverse=True)
        for node in self.my_inner_nodes:
            if node.max_leave <= 0:
                continue
            reserve = node.max_leave
            neighbours = node.links.links
            neighbours.sort(key=lambda x: x.node.max_leave)
            for neighbour in neighbours:
                if reserve <= neighbour.node.max_leave:
                    break
                # FIXME NOT max_leave, but power_on_max_distance
                move = (reserve + neighbour.node.max_leave) // 2
                self.moves.make_turn(Move(node.id, neighbour.node.id, move))
                node.incoming_troop(Troop(MY, -move, 0))
                neighbour.node.incoming_troop(Troop(MY, move, 0))
                if neighbour.node.max_leave <= 1:
                    neighbour.node.calculate_max_leave()
                else:
                    neighbour.node.max_leave += move
            node.max_leave = reserve
