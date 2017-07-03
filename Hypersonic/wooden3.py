# https://www.codingame.com/ide/puzzle/hypersonic

import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

BOMB_RANGE = 2
BOMB_TIMER = 8
MAX_BOMBS = 1

WIDTH = 13
HEIGHT = 11

LEFT = [-1, 0]
RIGHT = [1, 0]
UP = [0, -1]
DOWN = [0, 1]
DIRECTIONS = [LEFT, RIGHT, UP, DOWN]


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_direction(self, direction):
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]
        if new_x < 0 or new_x > WIDTH - 1:
            return None
        if new_y < 0 or new_y > HEIGHT - 1:
            return None
        return Point(new_x, new_y)

    def get_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __hash__(self):
        return self.x * HEIGHT + self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "{} {}".format(self.x, self.y)


class Player:
    def __init__(self, player_id, bomb_range=BOMB_RANGE):
        self.id = player_id
        self.position = None
        self.bombs = MAX_BOMBS
        self.bomb_range = bomb_range

    def update(self, position, bombs):
        self.position = position
        self.bombs = bombs


class Crate:
    def __init__(self, position, game_field):
        self.position = position
        self.valid = True
        self.field = game_field

    def invalidate(self):
        self.valid = False


class Bomb:
    def __init__(self, position, timer, range=BOMB_RANGE):
        self.position = position
        self.timer = timer
        self.range = range


EMPTY = "."
CRATE = "0"
BOMB = "B"
ENEMY = "E"
ME = "M"


class FieldElement:
    def __init__(self, position, game_field):
        self.position = position
        self.field = game_field
        self.type = ENEMY
        self.obj = None
        self.potential = 0

    def update(self, obj_type, obj=None):
        self.type = obj_type
        self.obj = obj
        self.potential = 0


class Turn:
    def __init__(self):
        self.bomb = False
        self.position = None

    def plant_bomb(self):
        self.bomb = True

    def move_to(self, position):
        self.position = position

    def __str__(self):
        return "{} {}".format("BOMB" if self.bomb else "MOVE", self.position)


class Field:
    def __init__(self):
        self.field = {}
        for i in range(WIDTH):
            for j in range(HEIGHT):
                position = Point(i, j)
                self.field[position] = FieldElement(position, self)
        self.crates = []
        self.bombs = []

    def start_turn(self):
        self.crates = []
        self.bombs = []

    def update(self, position, field_type, obj=None):
        if field_type == CRATE:
            if obj is None:
                obj = Crate(position, self)
            self.crates.append(obj)
        elif field_type == BOMB:
            self.bombs.append(obj)
        self.field[position].update(field_type, obj)

    def finalize_field(self):
        for bomb in self.bombs:
            for direction in DIRECTIONS:
                position = bomb.position
                for i in range(BOMB_RANGE):
                    position = position.get_direction(direction)
                    if position is None:
                        break
                    local_field = self.field[position]
                    if local_field.type == CRATE:
                        local_field.obj.invalidate()
                        break
        for crate in self.crates:
            if not crate.valid:
                continue
            for direction in DIRECTIONS:
                position = crate.position
                for i in range(BOMB_RANGE):
                    position = position.get_direction(direction)
                    if position is None:
                        break
                    local_field = self.field[position]
                    if local_field.type == CRATE:
                        local_field.obj.invalidate()
                        break
                    local_field.potential += 1
        turn = Turn()
        if me.bombs > 0 and self.field[me.position].potential > 0:
            turn.plant_bomb()

        best_position = None
        potential = -1
        distance = math.inf
        for i in range(WIDTH):
            for j in range(HEIGHT):
                point = Point(i, j)
                new_distance = point.get_distance(me.position)
                if potential < self.field[point].potential and \
                        (new_distance < BOMB_TIMER + BOMB_RANGE or distance > BOMB_TIMER + BOMB_RANGE):
                    best_position = point
                    potential = self.field[point].potential
                    distance = new_distance
                elif potential == self.field[point].potential and new_distance < distance:
                    best_position = point
                    potential = self.field[point].potential
                    distance = new_distance
        turn.move_to(best_position)
        return turn


*_, my_id = [int(i) for i in input().split()]

me = Player(my_id)
enemy = Player(0 if my_id == 0 else 1)

field = Field()

# game loop
while True:
    field.start_turn()
    for j in range(HEIGHT):
        row = input()
        for i in range(WIDTH):
            field.update(Point(i, j), row[i])
    entities = int(input())
    for i in range(entities):
        entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
        if entity_type == 0:
            if owner == my_id:
                me.update(Point(x, y), param_1)
                field.update(me.position, ME, me)
            else:
                enemy.update(Point(x, y), param_1)
                field.update(enemy.position, ENEMY, enemy)
        else:
            input_bomb = Bomb(Point(x, y), param_1)
            field.update(input_bomb.position, BOMB, input_bomb)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    print(field.finalize_field())
