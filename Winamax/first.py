# https://www.codingame.com/ide/puzzle/winamax-sponsored-contest

import sys
import math
import copy

HOLE = "H"
HAZARD = "X"
EMPTY = "."

UP = "^"
DOWN = "v"
LEFT = "<"
RIGHT = ">"

DIRECTIONS = {
    UP: [0, -1],
    DOWN: [0, 1],
    LEFT: [-1, 0],
    RIGHT: [1, 0]
}


class Map:
    def __init__(self, field_data, size):
        self.field = field_data
        self.size = size
        self.balls = []
        self.holes = []
        self._clean()

    def clone(self):
        return copy.deepcopy(self)

    def _clean(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.field[i][j] == HOLE:
                    self.field[i][j] = Hole(i, j)
                    self.holes.append(self.field[i][j])
                elif self.field[i][j].isdigit():
                    self.field[i][j] = Ball(int(self.field[i][j]), i, j, self)
                    self.balls.append(self.field[i][j])

    def isvalid(self, point):
        return 0 <= point[0] < self.size[0] and 0 <= point[1] < self.size[1]

    def build_paths(self):
        for ball in self.balls:
            ball.build_paths()

    def move_imagenary(self, path, direction, power, hard=False):
        modifier = DIRECTIONS[direction]
        last_point = path.get_end()
        new_point = [last_point[i] + power * modifier[i] for i in range(2)]
        if not self.field.isvalid(new_point):
            path.invalidate()
            return

class Path:
    def __init__(self, start):
        self.finished = False
        self.valid = True
        self.path = [start]

    def clone(self):
        return copy.deepcopy(self)

    def get_end(self):
        return self.path[-1]

    def add_point(self, point):
        self.path.append(point)

    def invalidate(self):
        self.valid = False

    def finish(self):
        self.finished = True


class Ball:
    def __init__(self, power, x, y, ball_field):
        self.field = ball_field
        self.power = power
        self.x = x
        self.y = y
        self.paths = []

    def build_paths(self):
        base_path = Path(start=[self.x, self.y])


class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y


width, height = [int(i) for i in input().split()]
MAP_BOUNDS = [[0, 0], [width, height]]
transposed_field = [list(input()) for i in range(height)]

field = Map(list(map(list, zip(*transposed_field))), [width, height])
