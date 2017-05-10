from GhostInTheShell.Bot3.events import *


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
