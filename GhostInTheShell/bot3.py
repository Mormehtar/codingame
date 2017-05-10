# https://www.codingame.com/ide/puzzle/ghost-in-the-cell
import math

# Settings
MAX_BOMBS = 2
MAX_DISTANCE = 20

# Owners
ENEMY = -1
NEUTRAL = 0
MY = 1

# Entities
FACTORY = 'FACTORY'
TROOP = 'TROOP'
BOMB = 'BOMB'

# Commands
WAIT = 'WAIT'
MOVE = 'MOVE'
BOMB = 'BOMB'
WAIT = 'WAIT'


class Statistics:
    def __init__(self, nodes):
        self.nodes = nodes
        self.mean_distance = 0
        self.min_distance = 0
        self.max_distance = 0

        self._links = 0
        self._total_distance = 0

        self._min_distances = [[math.inf for _ in range(nodes)] for _ in range(nodes)]
        self._distances = [[math.inf for _ in range(nodes)] for _ in range(nodes)]

        self.nodes = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }

        self.production = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }

        self.cyborgs = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }


class State:
    def __init__(self):
        self.my_bombs = MAX_BOMBS
        self.enemy_bombs = MAX_BOMBS

        self._enemy_bombs_in_process = {}

    def track_enemy_bomb(self, source, eta):
        track_bomb = self._enemy_bombs_in_process.get(source)
        if track_bomb is None:
            self.enemy_bombs -= 1
            self._enemy_bombs_in_process[source] = [eta]
            return
        if eta not in track_bomb:
            self.enemy_bombs -= 1
            self._enemy_bombs_in_process[source].append(eta)

    def end_input(self):
        sources_to_delete = []
        for source, track_bomb in self._enemy_bombs_in_process:
            track_bomb = [eta-1 for eta in track_bomb if eta > 1]
            if len(track_bomb) == 0:
                sources_to_delete.append(source)
            else:
                self._enemy_bombs_in_process[source] = track_bomb
        for source_to_delete in sources_to_delete:
            del self._enemy_bombs_in_process[source_to_delete]

    def trigger_my_bomb(self):
        self.my_bombs -= 1


class Event:
    def __init__(self, owner, eta):
        self.owner = owner
        self.eta = eta


class Troop(Event):
    def __init__(self, owner, cyborgs, eta):
        super().__init__(owner, eta)
        self.cyborgs = cyborgs


class Bomb(Event):
    pass


class Events:
    def __init__(self):
        self.event_turns = set()
        self.sorted_events = []
        self.events = {}

    def add_event(self, event):
        self.event_turns.add(event.eta)
        if self.events.get(event.eta) is None:
            self.events[event.eta] = []
        self.events[event.eta].append(event)

    def end_input(self):
        self.sorted_events = list(self.event_turns)
        self.sorted_events.sort()


class Link:
    def __init__(self, node, distance):
        self.node = node
        self.distance = distance


class Links:
    def __init__(self, node):
        self.node = node
        self.links = []

    def add_link(self, node, distance):
        self.links.append(Link(node, distance))


class NodeCore:
    def __init__(self, node, owner, cyborgs, production, repairing):
        self.node = node
        self.owner = owner
        self.cyborgs = cyborgs
        self.production = production
        self.repairing = repairing


class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.core = None
        self.incoming_events = Events()
        self.links = Links(self)

    def update(self, node_core):
        self.core = node_core

    def link(self, target, distance):
        self.links.add_link(target, distance)

    def incoming_troop(self, troop):
        self.incoming_events.add_event(troop)

    def incoming_bomb(self, bomb):
        self.incoming_events.add_event(bomb)

    def end_input(self):
        self.incoming_events.end_input()

    def start_turn(self):
        self.incoming_events = Events()


class Field:
    def __init__(self, nodes):
        self.nodes = [Node(i) for i in range(nodes)]
        self.state = State()

    def connect(self, node_index1, node_index2, distance):
        node1 = self.nodes[node_index1]
        node2 = self.nodes[node_index2]
        node1.link(node2, distance)
        node2.link(node1, distance)

    def start_turn(self):
        [node.start_turn() for node in self.nodes]

    def end_input(self):
        [node.end_input() for node in self.nodes]
        self.state.end_input()

    def update_factory(self, node_id, owner, cyborgs, production, repairing):
        self.nodes[node_id].update(NodeCore(owner, cyborgs, production, repairing))

    def update_troop(self, owner, target, cyborgs, eta):
        self.nodes[target].incoming_troop(Troop(owner, cyborgs, eta))

    def update_bomb(self, owner, source, target, eta):
        if target == 1:
            self.state.track_enemy_bomb(source, eta)
        self.nodes[target].incoming_bomb(Bomb(owner, eta))

    def choose_move(self):
        raise Exception('Not implemented yet')


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
        if entity_type == FACTORY:
            field.update_factory(entity_id, arg_1, arg_2, arg_3, arg_4)
        elif entity_type == TROOP:
            field.update_troop(arg_1, arg_3, arg_4, arg_5)
        elif entity_type == BOMB:
            field.update_bomb(arg_1, arg_3, arg_4)

    field.end_input()
    # print(field.choose_move())
    # print(message, file=sys.stderr)
    print(WAIT)
