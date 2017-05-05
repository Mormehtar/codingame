# https://www.codingame.com/ide/puzzle/coders-strike-back

import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


# game loop

has_boost = True
inertia = 1 - 0.15
prevX, prevY = None, None
prevOX, prevOY = None, None
boost = 650
checkpoint_radius = 600
bike_radius = 400
max_thrust = 100
engines_not_work = 0
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle\
        = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]
    engines_not_work -= 1
    if prevX is None:
        prevX = x
    if prevY is None:
        prevY = y
    velocity = math.sqrt(math.pow(x - prevX, 2) + math.pow(y - prevY, 2))
    new_velocity = velocity * inertia
    new_x = (x - prevX) * new_velocity
    new_y = (y - prevY) * new_velocity

    if prevOX is None:
        prevOX = x
    if prevOY is None:
        prevOY = y
    o_velocity = math.sqrt(math.pow(opponent_x - prevOX, 2) + math.pow(opponent_y - prevOY, 2))
    o_new_velocity = o_velocity * inertia

    new_o_x = (opponent_x - prevOX) * o_new_velocity
    new_o_y = (opponent_y - prevOY) * o_new_velocity

    # Write an action using print
    # To debug: print >> sys.stderr, "Debug messages..."


    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"

    projection = math.cos(math.radians(next_checkpoint_angle))
    angle = abs(next_checkpoint_angle)

    thrust = int(math.sqrt(max(projection, 0)) * max_thrust)
    # if angle > 90:
    #     thrust = 0
    # else:
    #    thrust = max(min(100, next_checkpoint_dist-600), 0)

    # print >> sys.stderr, x, y

    real_thrust = thrust

    # real_new_x = new_x + realthrust * (next_checkpoint_x - x) / next_checkpoint_dist
    # real_new_y = new_y + realthrust * (next_checkpoint_y - y) / next_checkpoint_dist

    # real_new_distance = math.sqrt(math.pow(new_o_x - real_new_x, 2) + math.pow(new_o_y - real_new_y, 2))
    inertial_new_distance = math.sqrt(math.pow(new_o_x - new_x, 2) + math.pow(new_o_y - new_y, 2))
    start_distance = math.sqrt(math.pow(x - new_x, 2) + math.pow(y - new_y, 2))

    if new_velocity > 0 and min(inertial_new_distance, start_distance) < 2 * bike_radius + max_thrust:
        thrust = "SHIELD"
        real_thrust = 0
        engines_not_work = 3

    if has_boost and angle == 0 and next_checkpoint_dist > (real_thrust + checkpoint_radius) and engines_not_work <= 0:
        thrust = "BOOST"
        real_thrust = boost
        has_boost = False

    print(next_checkpoint_x, next_checkpoint_y, thrust)
    prevX, prevY = x, y
    prevOX, prevOY = opponent_x, opponent_y
