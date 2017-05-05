# https://www.codingame.com/ide/puzzle/shadows-of-the-knight-episode-1

import sys
import math

UP = 'U'
UP_RIGHT = 'UR'
RIGHT = 'R'
DOWN_RIGHT = 'DR'
DOWN = 'D'
DOWN_LEFT = 'DL'
LEFT = 'L'
UP_LEFT = 'UL'

CUTTERS = {
    UP: [1, 0, 1, 1],
    UP_RIGHT: [1, 0, 0, 1],
    RIGHT: [1, 1, 0, 1],
    DOWN_RIGHT: [1, 1, 0, 0],
    DOWN: [1, 1, 1, 0],
    DOWN_LEFT: [0, 1, 1, 0],
    LEFT: [0, 1, 1, 1],
    UP_LEFT: [0, 0, 1, 1]
}


def cut(field, position, direction):
    template = CUTTERS[direction]
    positions = position + position
    return [field[i] * (1 - template[i]) + positions[i] * template[i] for i in range(4)]


def next_move(field):
    return [(field[i] + field[i + 2]) // 2 for i in range(2)]

# w: width of the building.
# h: height of the building.
w, h = [int(i) for i in input().split()]
n = int(input())  # maximum number of turns before game over.
turn = [int(i) for i in input().split()]

game_field = [0, 0, w, h]

# game loop
while True:
    bomb_dir = input()  # the direction of the bombs from batman's current location (U, UR, R, DR, D, DL, L or UL)
    game_field = cut(game_field, turn, bomb_dir)
    turn = next_move(game_field)
    print('{} {}'.format(*turn))
