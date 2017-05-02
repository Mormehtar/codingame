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
                    self.field[i][j] = Ball(int(self.field[i][j]), i, j)
                    self.balls.append(self.field[i][j])

    def isvalid(self, point):
        return 0 <= point[0] < self.size[0] and 0 <= point[1] < self.size[1]

    def _build_possible_paths(self, power, path, last_direction=None):
        directions = [direction for direction in DIRECTIONS.keys() if direction != last_direction]
        output = []
        for direction in directions:
            new_path = self.check_move(path, direction, power)
            if not new_path.valid:
                continue
            if new_path.is_finished():
                output.append(new_path)
                continue
            output += self._build_possible_paths(power - 1, new_path, direction)
        return output

    def build_paths(self):
        for ball in self.balls:
            ball.load_paths(self._build_possible_paths(ball.power, Path([ball.x, ball.y])))
        self.balls.sort(key=lambda a: len(a.paths))
        for ball in self.balls:
            ball.paths.sort(key=lambda a: a.hole.weight)

    def check_move(self, path, direction, power):
        modifier = DIRECTIONS[direction]
        last_point = path.get_end()
        new_point = [last_point[i] + power * modifier[i] for i in range(2)]
        if not self.field.isvalid(new_point):
            path.invalidate()
        else:
            target = self.field[new_point[0]][new_point[1]]
            if target is Hole:
                path.reach(new_point, target)
                target.increase_weight()
            elif target == HAZARD or target.isdigit:
                path.invalidate()
            else:
                path.add_point(new_point)
        return path

    def search_valid_path(self):
        ball_index = 0
        path_index = 0
        valid_path = None
        while valid_path is None and 0 <= ball_index < len(self.balls):
            step_valid = self.implement_path(self.balls[ball_index].path[path_index])


class Path:
    def __init__(self, start):
        self.valid = True
        self.hole = None
        self.path = [start]

    def clone(self):
        return copy.deepcopy(self)

    def get_end(self):
        return self.path[-1]

    def add_point(self, point):
        self.path.append(point)

    def invalidate(self):
        self.valid = False

    def reach(self, point, hole):
        self.add_point(point)
        self.hole = hole

    def is_finished(self):
        return self.hole is not None


class Ball:
    def __init__(self, power, x, y):
        self.power = power
        self.x = x
        self.y = y
        self.paths = []

    def load_paths(self, paths):
        self.paths = paths


class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.weight = 0
        self.filled = False

    def increase_weight(self):
        self.weight += 1


width, height = [int(i) for i in input().split()]
MAP_BOUNDS = [[0, 0], [width, height]]
transposed_field = [list(input()) for i in range(height)]

field = Map(list(map(list, zip(*transposed_field))), [width, height])
field.build_paths()

