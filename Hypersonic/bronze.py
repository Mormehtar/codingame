# https://www.codingame.com/ide/puzzle/hypersonic

import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

BOMB_RANGE = 3
BOMB_TIMER = 8
MAX_BOMBS = 1

MAX_WIDTH = 13
MAX_HEIGHT = 11


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{} {}".format(self.x, self.y)

    def __hash__(self):
        return self.x * MAX_HEIGHT + self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


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


class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.bombs = MAX_BOMBS
        self.bomb_range = BOMB_RANGE
        self.position = None

    def update(self, position, bombs, bomb_range):
        self.position = position
        self.bombs = bombs
        self.bomb_range = bomb_range


class Bomb:
    def __init__(self, owner, position, timer, bomb_range):
        self.owner = owner
        self.position = position
        self.timer = timer
        self.range = bomb_range
        self.conglomerate = None

    def add_to_conglomerate(self, conglomerate):
        self.conglomerate = conglomerate
        conglomerate.add_bomb(self)

    def is_in_conglamerate(self):
        return not self.conglomerate is None


class Item:
    def __init__(self, position, item_type):
        self.position = position
        self.type = item_type


class FieldPoint:

    EMPTY = "."
    WALL = "X"
    EMPTY_CRATE = "0"

    def __init__(self, position, field):
        self.position = position
        self.field = field
        self.type = self.EMPTY
        self.obj = None
        self.trajectory = math.inf
        self.exploded = False
        self.priority = -math.inf

    def update(self, field_type):
        self.type = field_type
        self.obj = None
        self.trajectory = math.inf
        self.exploded = False
        self.priority = -math.inf

    def update_with_object(self, obj):
        self.obj = obj

    def is_empty(self):
        return self.obj is None and self.type == self.EMPTY

    def is_crate(self):
        return self.type.isdigit()

    def is_empty_crate(self):
        return self.type == self.EMPTY_CRATE

    def is_crate_with_item(self):
        return self.is_crate() and not self.is_empty_crate()

    def is_bomb(self):
        return type(self.obj) is Bomb

    def is_item(self):
        return type(self.obj) is Item

    def is_player(self):
        return type(self.obj) is Player

    def is_wall(self):
        return self.type == self.WALL

    def is_impassable(self):
        return self.is_crate() or self.is_bomb() or self.is_wall()


class BombConglamerate:
    def __init__(self, field):
        self.bombs = []
        self.timer = math.inf
        self.field = field

    def add_bomb(self, bomb):
        self.bombs.append(bomb)
        self.timer = min(self.timer, bomb.timer)


class Field:

    LEFT = [-1, 0]
    RIGHT = [1, 0]
    UP = [0, -1]
    DOWN = [0, 1]
    DIRECTIONS = [LEFT, RIGHT, UP, DOWN]

    EMPTY_CRATE_PRIORITY = 8
    ITEM_CRATE_PRIORITY = EMPTY_CRATE_PRIORITY * 2
    ITEM_PRIORITY = ITEM_CRATE_PRIORITY * 5
    ENEMY_PRIORITY = ITEM_CRATE_PRIORITY * 6

    BOMB_IN_FUTURE = 1
    BOMB_DANGER = -ITEM_CRATE_PRIORITY * 7

    def __init__(self, players, my_id, width, height):

        self.TYPES = {
            1: self.update_player,
            2: self.update_bomb,
            3: self.update_item
        }

        self.width = width
        self.height = height

        self.players = players
        self.me = players[my_id]
        self.enemies = [player for player in players if player.id != my_id]

        self.field = {}
        for x in range(width):
            for y in range(height):
                point = Point(x, y)
                self.field[point] = FieldPoint(Point(x, y), self)

        self.bombs = []
        self.bomb_conglomerates = []
        self.items = []
        self.crates = []

    def start_turn(self):
        self.bombs = []
        self.items = []
        self.bomb_conglomerates = []
        self.crates = []

    def get_direction(self, point, direction):
        new_x = point.x + direction[0]
        new_y = point.y + direction[1]
        if new_x < 0 or new_x > self.width - 1:
            return None
        if new_y < 0 or new_y > self.height - 1:
            return None
        return Point(new_x, new_y)

    def update_player(self, owner, position, bombs, bomb_range):
        self.players[owner].update(position, bombs, bomb_range)
        self.field[position].update_with_object(self.players[owner])

    def update_bomb(self, owner, position, timer, bomb_range):
        bomb = Bomb(owner, position, timer, bomb_range)
        self.bombs.append(bomb)
        self.field[position].update_with_object(bomb)

    def update_item(self, _, position, item_type, *args):
        item = Item(position, item_type)
        self.items.append(item)
        self.field[position].update_with_object(item)

    def update_object(self, entity_type, owner, position, param1, param2):
        return self.TYPES[entity_type](owner, position, param1, param2)

    def update_field(self, position, field_type):
        self.field[position].update(field_type)
        if self.field[position].is_crate():
            self.crates.append(position)

    def build_trajectories(self, points=None):
        if points is None:
            points = {self.me.position}
            self.field[self.me.position].trajectory = 0
        to_update = set()
        for point in points:
            field = self.field[point]
            distance = field.trajectory + 1
            for direction in self.DIRECTIONS:
                new_point = self.get_direction(point, direction)
                if new_point is None:
                    continue
                new_field = self.field[new_point]
                if new_field.trajectory > distance:
                    new_field.trajectory = distance
                    to_update.add(new_point)
        if len(to_update) > 0:
            self.build_trajectories(to_update)

    def build_bombs_conglomerates(self):
        for bomb in self.bombs:
            conglamerate = BombConglamerate(self)
            conglamerate.add_bomb(bomb)
            position = bomb.position
            for direction in self.DIRECTIONS:
                new_position = position
                for l in range(bomb.range - 1):
                    new_position = self.get_direction(new_position, direction)
                    if new_position is None:
                        break
                    field = self.field[new_position]
                    field.exploded = True
                    if field.is_bomb:
                        connected_bomb = field.obj
                        if connected_bomb.is_in_conglamerate():
                            c = connected_bomb.conglamerate
                            self.bomb_conglomerates.remove(c)
                            for inner_bomb in c:
                                conglamerate.add_bomb(inner_bomb)
                        else:
                            conglamerate.add_bomb(connected_bomb)
                        break
                    if field.is_impassable():
                        break
            self.bomb_conglomerates.append(conglamerate)

    def build_crates_priority(self):
        for crate_position in self.crates:
            crate_field = self.field[crate_position]
            if crate_field.exploded:
                continue
            for direction in self.DIRECTIONS:
                new_point = crate_position
                for l in range(self.me.range - 1):
                    new_point = self.get_direction(new_point, direction)
                    if new_point is None:
                        break
                    field = self.field[new_point]
                    if field.trajectory == math.inf:
                        break
                    if crate_field.is_empty_crate():
                        field.priority += self.EMPTY_CRATE_PRIORITY
                    else:
                        field.priority += self.ITEM_CRATE_PRIORITY

    def build_items_priority(self):
        for item in self.items:
            item_field = self.field[item.position]
            if item_field.trajectory == math.inf:
                continue
            item_field.priority += self.ITEM_PRIORITY

    def build_enemy_priority(self):
        for enemy in self.enemies:
            enemy_field = self.field[enemy.position]
            if enemy_field.exploded:
                continue
            for direction in self.DIRECTIONS:
                new_point = enemy.position
                for l in range(self.me.range - 1):
                    new_point = self.get_direction(new_point, direction)
                    if new_point is None:
                        break
                    field = self.field[new_point]
                    if field.trajectory == math.inf:
                        break
                    field.priority += self.ENEMY_PRIORITY

    def build_bombs_priorities(self):
        pass
    # TODO!

    def process_turn(self):
        self.build_trajectories()
        self.build_bombs_conglomerates()
        self.build_crates_priority()
        self.build_items_priority()
        self.build_enemy_priority()
        self.build_bombs_priorities()

def process_init():
    width, height, my_id = [int(i) for i in input().split()]
    return Field([Player(_id) for _id in range(4)], my_id, width, height)


def process_input(field):
    for j in range(MAX_HEIGHT):
        row = input()
        for i in range(MAX_WIDTH):
            field.update_field(Point(i, j), row[i])
    entities = int(input())
    for i in range(entities):
        entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
        field.update_object(entity_type, owner, Point(x, y), param_1, param_2)


def process_turn(field):
    field.start_turn()
    process_input(field)
    print(field.process_turn())


game_field = process_init()
while True:
    process_turn(game_field)