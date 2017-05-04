# https://www.codingame.com/ide/754479346cff2182d90fa4544d5708535eddec9

import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

skyline = [0] * 5000

min_x = 5000
max_x = 0

n = int(input())
for i in range(n):
    h, x_1, x_2 = [int(j) for j in input().split()]
    print(h, x_1, x_2, file=sys.stderr)
    for x in range(x_1, x_2 + 1):
        min_x = min(min_x, x_1)
        max_x = max(max_x, x_2)
        skyline[x] = max(skyline[x], h)

skyline = skyline[min_x : max_x]
lines = 3
now_h = skyline[0]
for h in skyline:
    if h != now_h:
        now_h = h
        lines += 2

# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr)

print(lines)
