# https://www.codingame.com/ide/puzzle/code-of-the-rings

ZONES = 30
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
START = LETTERS.index(" ")
FIELD = [START] * ZONES

position = ZONES // 2

LEFT = "<"
RIGHT = ">"
UP = "+"
DOWN = "-"
USE = "."


def get_distance(x, y):
    up = (y - x) % len(LETTERS)
    down = len(LETTERS) - up
    return (up, UP) if up < down else (down, DOWN)

magic_phrase = list(input())


# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr)

result = []

while len(magic_phrase):
    letter = LETTERS.index(magic_phrase.pop(0))
    while FIELD[position] != letter:
        here, here_action = get_distance(FIELD[position], letter)
        right, _ = get_distance(FIELD[(position + 1) % ZONES], letter)
        left, _ = get_distance(FIELD[(position - 1) % ZONES], letter)
        if here <= min(right, left):
            if here_action == UP:
                FIELD[position] = (FIELD[position] + 1) % len(LETTERS)
            else:
                FIELD[position] = (FIELD[position] - 1) % len(LETTERS)
            result.append(here_action)
        elif right < left:
            result.append(RIGHT)
            position = (position + 1) % ZONES
        else:
            result.append(LEFT)
            position = (position - 1) % ZONES
    result.append(USE)

print("".join(result))
