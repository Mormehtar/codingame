from GhostInTheShell.Bot3.events import *
from GhostInTheShell.Bot3.links import *
from GhostInTheShell.Bot3.constants import *


class NodeCore:
    def __init__(self, node, owner, cyborgs, production, repairing):
        self.node = node
        self.owner = owner
        self.cyborgs = cyborgs
        self.production = production
        self.repairing = repairing

    def clone(self):
        return NodeCore(self.node, self.owner, self.cyborgs, self.production, self.repairing)

    def simulate_turns(self, turns):
        turns -= self.repairing
        if turns <= 0:
            self.repairing = -turns
        else:
            self.repairing = 0
            self.cyborgs += self.production * turns


class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.core = None
        self.incoming_events = Events()
        self.links = Links(self)
        self.is_border = False
        self.is_enemy_border = False
        self.max_leave = 0
        self.bordering = set()
        self.max_distance = 0
        self.power_on_max_distance = 0

    def update(self, node_core):
        self.core = node_core

    def link(self, target, distance):
        self.links.add_link(target, distance)

    def incoming_troop(self, troop):
        self.incoming_events.add_event(troop)

    def incoming_bomb(self, bomb):
        self.incoming_events.add_event(bomb)

    def end_init(self, statistics):
        self.max_distance = statistics.max_distance

    def end_input(self):
        self.incoming_events.end_input()
        self.check_if_border()

    def calculate_max_leave(self):
        self.max_leave = self.incoming_events.calculate_max_leave(self.core) if self.core.owner == MY else 0

    def start_turn(self):
        self.incoming_events = Events()

    def check_if_border(self):
        self.is_border = False
        self.is_enemy_border = False
        self.bordering = set()
        for neighbour in self.links.get_neighbours():
            if neighbour.core.owner != self.core.owner:
                self.bordering.add(neighbour.core.owner)
                self.is_border = True
                if neighbour.core.owner != NEUTRAL:
                    self.is_enemy_border = True
            if len(self.bordering) == 2:
                return

    def calculate_power_on_max_distance(self):
        state = self.incoming_events.calculate_state_on_distance(self.core, self.max_distance)
        self.power_on_max_distance = state.owner * self.owner * state.cyborgs
