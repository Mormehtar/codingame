# https://www.codingame.com/ide/puzzle/hypersonic

import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

BOMB_RANGE = 3
BOMB_TIMER = 8
MAX_BOMBS = 1

WIDTH = 13
HEIGHT = 11

LEFT = [-1, 0]
RIGHT = [1, 0]
UP = [0, -1]
DOWN = [0, 1]
DIRECTIONS = [LEFT, RIGHT, UP, DOWN]

CRATE_MODIFIER = 8
CRATE_ITEM_MODIFIER = 1
BOMB_MODIFIER = 1
ITEM_MODIFIER = 8 * 5


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

    def update(self, position, bombs, bomb_range):
        self.position = position
        self.bombs = bombs
        self.bomb_range = bomb_range


class Crate:
    def __init__(self, position, crate_type, game_field):
        self.position = position
        self.valid = True
        self.field = game_field
        self.type = crate_type

    def invalidate(self):
        self.valid = False


class Bomb:
    def __init__(self, position, timer, bomb_range=BOMB_RANGE):
        self.position = position
        self.timer = timer
        self.bomb_range = bomb_range


EMPTY = "."
EMPTY_CRATE = "0"
CRATE_ITEM = "1"
CRATE_ITEM2 = "2"
BOMB = "B"
ENEMY = "E"
ME = "M"
ITEM = "I"


class Item:
    def __init__(self, position, item_type):
        self.position = position
        self.type = item_type


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
        self.items = []

    def start_turn(self):
        self.crates = []
        self.bombs = []
        self.items = []

    def update(self, position, field_type, obj=None):
        print("update", position, field_type, file=sys.stderr)
        if field_type == EMPTY_CRATE or field_type == CRATE_ITEM or field_type == CRATE_ITEM2:
            field_type = EMPTY_CRATE
            if obj is None:
                obj = Crate(position, field_type, self)
            self.crates.append(obj)
            print("I'm crate!", file=sys.stderr)
        elif field_type == BOMB:
            self.bombs.append(obj)
            print("I'm bomb!", file=sys.stderr)
        elif field_type == ITEM:
            self.items.append(obj)
            print("I'm item!", file=sys.stderr)
        self.field[position].update(field_type, obj)

    def finalize_field(self):
        print('bombs', len(self.bombs), file=sys.stderr)
        print('crates', len(self.crates), file=sys.stderr)
        print('items', len(self.items), file=sys.stderr)
        for bomb in self.bombs:
            print("BOMB!", bomb.position, file=sys.stderr)
            for direction in DIRECTIONS:
                position = bomb.position
                for i in range(bomb.bomb_range - 1):
                    position = position.get_direction(direction)
                    if position is None:
                        break
                    local_field = self.field[position]
                    if local_field.type == EMPTY_CRATE:
                        local_field.obj.invalidate()
                        break
                    if local_field.type == BOMB:
                        break
                    local_field.potential += (BOMB_TIMER - bomb.timer) * BOMB_MODIFIER
        for crate in self.crates:
            print("CRATE!", crate.position, crate.valid, file=sys.stderr)
            if not crate.valid:
                continue
            for direction in DIRECTIONS:
                position = crate.position
                for i in range(me.bomb_range - 1):
                    position = position.get_direction(direction)
                    if position is None:
                        break
                    local_field = self.field[position]
                    if local_field.type == EMPTY_CRATE:
                        break
                    local_field.potential += CRATE_MODIFIER
                    if crate.type != EMPTY_CRATE:
                        local_field.potential += CRATE_ITEM_MODIFIER
        for item in self.items:
            print("ITEM!", item.position, file=sys.stderr)
            self.field[item.position].potential = ITEM_MODIFIER
        turn = Turn()
        print("DO YOU WANNA BOMB?", me.bombs, self.field[me.position].potential, file=sys.stderr)
        if me.bombs > 0 and self.field[me.position].potential >= CRATE_MODIFIER:
            turn.plant_bomb()

        best_position = None
        potential = -1
        distance = math.inf
        for i in range(WIDTH):
            for j in range(HEIGHT):
                point = Point(i, j)
                new_distance = point.get_distance(me.position)
                if potential < self.field[point].potential and \
                        (new_distance < BOMB_TIMER + me.bomb_range - 1 or distance > BOMB_TIMER + me.bomb_range - 1):
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
                me.update(Point(x, y), param_1, param_2)
                field.update(me.position, ME, me)
            else:
                enemy.update(Point(x, y), param_1, param_2)
                field.update(enemy.position, ENEMY, enemy)
        elif entity_type == 1:
            input_bomb = Bomb(Point(x, y), param_1, param_2)
            field.update(input_bomb.position, BOMB, input_bomb)
        else:
            input_item = Item(Point(x, y), param_1)
            field.update(input_item.position, ITEM, input_item)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    print(field.finalize_field())
