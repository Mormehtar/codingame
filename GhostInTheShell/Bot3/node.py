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
        self.max_leave = 0

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
        self.check_if_border()
        self.max_leave = self.incoming_events.calculate_max_leave(self.core) if self.core.owner == MY else 0

    def start_turn(self):
        self.incoming_events = Events()

    def check_if_border(self):
        self.is_border = not all(
            map(lambda neighbour: neighbour.core.owner == self.core.owner, self.links.get_neighbours())
        )
