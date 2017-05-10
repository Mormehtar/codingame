# https://www.codingame.com/ide/puzzle/ghost-in-the-cell
import math

MAX_DISTANCE = 20

ENEMY = -1
NEUTRAL = 0
MY = 1


class Turn():
    def __init__(self, cyborgs=0, value=0, node1=None, node2=None):
        self.node1 = node1
        self.node2 = node2
        self.cyborgs = cyborgs
        self.value = value

    def __str__(self):
        if self.node1 is None or self.node2 is None or self.cyborgs <= 0:
            return 'WAIT'
        return 'MOVE {} {} {}'.format(self.node1.id, self.node2.id, self.cyborgs)


class Troop:
    def __init__(self, owner, cyborgs, eta):
        self.owner = owner
        self.cyborgs = cyborgs
        self.eta = eta


class Node:
    def __init__(self, index):
        self.id = index
        self.owner = NEUTRAL
        self.cyborgs = 0
        self.production = 0
        self.incoming = []
        self.new_cyborgs = {}
        self.links = []

    def add_link(self, node, distance):
        self.links.append([node, distance])

    def update(self, owner, cyborgs, production):
        self.owner = owner
        self.cyborgs = cyborgs
        self.production = production

    def send_troops(self, troop):
        self.incoming.append(troop)
        if self.new_cyborgs.get(troop.eta) is None:
            self.new_cyborgs[troop.eta] = []
        self.new_cyborgs[troop.eta].append(troop)

    def start_turn(self):
        self.incoming = []
        self.new_cyborgs = {}

    def get_max_leave(self):
        if self.cyborgs == 0:
            return 0
        turns = [i for i in self.new_cyborgs.keys()]
        turns.sort()
        turns.insert(0, 0)
        last_turn = 0
        max_leave = self.cyborgs
        cyborgs = 0
        for turn in turns:
            cyborgs += (turn - last_turn) * self.production
            if self.new_cyborgs.get(turn) is not None:
                for troop in self.new_cyborgs[turn]:
                    if troop.owner != self.owner:
                        cyborgs -= troop.cyborgs
                    else:
                        cyborgs += troop.cyborgs
            if cyborgs < 0:
                max_leave += cyborgs
                cyborgs = 0
            if max_leave < 0:
                return 0
            last_turn = turn
        return max_leave

    def get_min_invade(self, distance):
        state_at_distance = self.get_state_on_distance(distance)
        turns = [i for i in self.new_cyborgs.keys() if i > distance]
        turns.sort()
        turns.insert(0, distance)
        last_turn = distance
        if state_at_distance["owner"] == MY:
            min_invade = 0
            cyborgs = state_at_distance["cyborgs"]
        else:
            min_invade = state_at_distance["cyborgs"]
            cyborgs = 0
        for turn in turns:
            cyborgs += (turn - last_turn) * self.production
            if self.new_cyborgs.get(turn) is not None:
                for troop in self.new_cyborgs[turn]:
                    if troop.owner != self.owner:
                        cyborgs -= troop.cyborgs
                    else:
                        cyborgs += troop.cyborgs
                    if cyborgs < 0:
                        min_invade -= cyborgs
                        cyborgs = 0
            last_turn = turn
        return min_invade

    def get_incomes(self, income):
        if income is None:
            return self.new_cyborgs
        new_cyborgs = self.new_cyborgs.copy()
        if new_cyborgs.get(income.eta) is None:
            new_cyborgs[income.eta] = [income]
            return new_cyborgs
        new_cyborgs[income.eta] = new_cyborgs[income.eta].copy() + [income]
        return new_cyborgs

    def get_state_on_distance(self, distance, income=None, outcome=0):
        new_cyborgs = self.get_incomes(income)
        turns = [i for i in new_cyborgs.keys() if i < distance]
        turns.sort()
        turns.append(distance)
        last_turn = 0
        owner = self.owner
        cyborgs = self.cyborgs - outcome
        for turn in turns:
            if owner != NEUTRAL:
                cyborgs += (turn - last_turn) * self.production
            my_troops = 0
            enemy_troops = 0
            if new_cyborgs.get(turn) is not None:
                for troop in new_cyborgs[turn]:
                    if troop.owner == MY:
                        my_troops += troop.cyborgs
                    else:
                        enemy_troops += troop.cyborgs
            if owner == MY:
                cyborgs += my_troops - enemy_troops
            elif owner == ENEMY:
                cyborgs += enemy_troops - my_troops
            else:
                cyborgs -= abs(my_troops - enemy_troops)
            if cyborgs < 0:
                owner = MY if my_troops > enemy_troops else ENEMY
        return {
            "owner": owner,
            "cyborgs": cyborgs
        }


class Field:
    def __init__(self, nodes_number):
        self.node_number = nodes_number
        self.my_nodes = []
        self.neutral_nodes = []
        self.enemy_nodes = []
        self.nodes = [Node(i) for i in range(nodes_number)]
        self.links = [[math.inf for _ in range(nodes_number)] for _ in range(nodes_number)]
        self.link_dict = {}
        self.total_distance = 0
        self.total_links = 0
        self.mean_distance = 0
        self.strategies = [
            self.min_invade_strategy
        ]

    def connect(self, node1_index, node2_index, distance):
        self.total_distance += distance
        self.total_links += 1
        self.mean_distance = self.total_distance / self.total_links
        self.links[node1_index][node2_index] = self.links[node2_index][node1_index] = distance
        node1 = self.nodes[node1_index]
        node2 = self.nodes[node2_index]
        node1.add_link(node2, distance)
        node2.add_link(node1, distance)

    def start_turn(self):
        self.my_nodes = []
        self.neutral_nodes = []
        self.enemy_nodes = []
        for node in self.nodes:
            node.start_turn()

    def update_factory(self, node_index, owner, cyborgs, production):
        node = self.nodes[node_index]
        node.update(owner, cyborgs, production)
        if node.owner == MY:
            self.my_nodes.append(node)
        elif node.owner == ENEMY:
            self.enemy_nodes.append(node)
        else:
            self.neutral_nodes.append(node)

    def update_troop(self, owner, node_index, cyborgs, eta):
        troop = Troop(owner, cyborgs, eta)
        node = self.nodes[node_index]
        node.send_troops(troop)

    def build_values(self, node1, node2):
        max_leave = node1.get_max_leave()
        min_invade = node2.get_min_invade(self.links[node1.id][node2.id])
        return [
            Turn(i[0], i[1], node1, node2)
            for i in [strategy(node1, node2, min_invade, max_leave) for strategy in self.strategies] if i[0] > 0
        ]

    def min_invade_strategy(self, node1, node2, min_leave, max_invade):
        if min_leave <= 0:
            return [0, -math.inf]
        return [min_leave, self.get_invade_result(node1, node2, min_leave, MAX_DISTANCE)]

    def get_invade_result(self, node1, node2, cyborgs, horizon):
        distance = self.links[node1.id][node2.id]
        res1 = node1.get_state_on_distance(horizon, outcome=cyborgs)
        res2 = node2.get_state_on_distance(horizon, income=Troop(MY, cyborgs, distance))
        base1 = node1.get_state_on_distance(horizon)
        base2 = node2.get_state_on_distance(horizon)
        return self.get_value(base1) + self.get_value(base2) + self.get_value(res1) + self.get_value(res2)

    def get_value(self, node):
        pure_value = node["owner"] * node["cyborgs"] if node["owner"] != NEUTRAL else node["cyborgs"]
        return pure_value

    def choose_move(self):
        turns = []
        for node1 in self.my_nodes:
            for link in node1.links:
                turns += self.build_values(node1, link[0])
        best_turn = Turn()
        for turn in turns:
            if best_turn.value < turn.value:
                best_turn = turn
        return best_turn


field = Field(int(input()))
for _ in range(int(input())):
    field.connect(*[int(j) for j in input().split()])

# game loop
while True:
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    field.start_turn()

    for _ in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        entity_id = int(entity_id)
        arg_1 = int(arg_1)
        arg_2 = int(arg_2)
        arg_3 = int(arg_3)
        arg_4 = int(arg_4)
        arg_5 = int(arg_5)
        if entity_type == 'FACTORY':
            field.update_factory(entity_id, arg_1, arg_2, arg_3)
        else:
            field.update_troop(arg_1, arg_3, arg_4, arg_5)

    print(field.choose_move())
