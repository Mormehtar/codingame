# https://www.codingame.com/ide/puzzle/there-is-no-spoon-episode-1

import sys
import math

# Don't let the machines win. You are humanity's last hope...
NODE = '0'


class Node:
    def __init__(self, node_x, node_y):
        self.node = [node_x, node_y]
        self.right = [-1, -1]
        self.bottom = [-1, -1]

    def __str__(self):
        return ' '.join([str(i) for i in self.node + self.right + self.bottom])

    def finish(self):
        print(self)


class NodePanel:
    def __init__(self, width):
        self.elments = [None] * width
        self.last_node = None

    def add_node(self, node):
        element = self.elments[node.node[0]]
        if element is None:
            self.elments[node.node[0]] = node
        else:
            element.bottom = node.node
            element.finish()
            self.elments[node.node[0]] = node
        if self.last_node is not None:
            self.last_node.right = node.node
        self.last_node = node

    def new_line(self):
        self.last_node = None

    def last_line(self):
        for node in self.elments:
            if node is not None:
                node.finish()


width = int(input())  # the number of cells on the X axis
height = int(input())  # the number of cells on the Y axis
node_panel = NodePanel(width)
for y in range(height):
    line = input()  # width characters, each either 0 or .
    for x in range(width):
        el = line[x]
        if el == NODE:
            node_panel.add_node(Node(x, y))
    node_panel.new_line()
node_panel.last_line()
