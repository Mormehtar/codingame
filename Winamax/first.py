# https://www.codingame.com/ide/puzzle/winamax-sponsored-contest

import sys
import math
import copy

DIRECTIONS = {
    "up": {"symbol": "^"},
    "down": {"symbol": "v"},
    "right": {"symbol": ">"},
    "left": {"symbol": "<"}
}

class Turn:
    def __init__(self, balls, holes, field):
        self.balls = copy.deepcopy(balls)
        self.holes = copy.deepcopy(holes)
        self.field = copy.deepcopy(field)

    def do_turn(self, direction):
        return

width, height = [int(i) for i in input().split()]
field = [list(input()) for i in range(height)]


