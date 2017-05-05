# https://www.codingame.com/ide/puzzle/skynet-revolution-episode-1

import sys
import math


class Node:
    def __init__(self, index):
        self.links = set()
        self.index = index
        self.gateway_link = None
        self.gateway = False

    def disconnect(self, node):
        self.links.discard(node)
        if self.gateway_link == node:
            self.gateway_link = None


class Graph:
    def __init__(self, node_number):
        self.nodes = [Node(i) for i in range(node_number)]

    def connect(self, index1, index2):
        a = self.nodes[index1]
        b = self.nodes[index2]
        a.links.add(b)
        b.links.add(a)

    def set_gateway(self, index):
        gateway = self.nodes[index]
        gateway.gateway = True
        for danger in gateway.links:
            danger.gateway_link = gateway

    def look_for_turn(self, virus_index):
        node = self.nodes[virus_index]
        if node.gateway_link is not None:
            return node.gateway_link
        max_power = 0
        max_node = None
        for element in node.links:
            node_power = len(element.links)
            if node_power > max_power:
                max_power = node_power
                max_node = element
        return max_node

    def disconnect(self, index1, index2):
        node1 = self.nodes[index1]
        node2 = self.nodes[index2]
        node1.disconnect(node2)
        node2.disconnect(node1)


def init():
    # n: the total number of nodes in the level, including the gateways
    # l: the number of links
    # e: the number of exit gateways
    n, l, e = [int(i) for i in input().split()]
    graph = Graph(n)
    for i in range(l):
        # n1: N1 and N2 defines a link between these nodes
        n1, n2 = [int(j) for j in input().split()]
        graph.connect(n1, n2)
    for i in range(e):
        ei = int(input())  # the index of a gateway node
        graph.set_gateway(ei)
    return graph


def game_loop(graph):
    # game loop
    while True:
        si = int(input())  # The index of the node on which the Skynet agent is positioned this turn
        node = graph.look_for_turn(si)
        turn = [si, node.index]
        graph.disconnect(*turn)
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        print('{} {}'.format(*turn))

game_loop(init())
