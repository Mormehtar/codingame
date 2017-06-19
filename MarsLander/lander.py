# https://www.codingame.com/ide/puzzle/mars-lander
import math

G = 3.711
MAX_VERTICAL_LANDING_SPEED = 20
MAX_HORIZONTAL_LANDING_SPEED = 40
MAX_ROTATION = 15
MAX_THRUST_CHANGE = 1


class Point:
    def __init__(self, point_x, point_y):
        self.x = point_x
        self.y = point_y


class Map:
    def __init__(self):
        self.map = []
        self.flat_left = None
        self.flat_right = None
        self.flat_height = None

    def add_point(self, point):
        self.map.append(point)

    def finish_init(self):
        self.map.sort(key=lambda p: p.x)
        _map = []
        found = False
        for point in self.map:
            if len(_map) == 0:
                _map.append(point)
                continue
            if point.y == _map[-1].y:
                if found:
                    self.flat_right = point.x
                else:
                    self.flat_left = _map[-1].x
                    self.flat_right = point.x
                    self.flat_height = point.y
            elif found and point.y < _map[-1].y:
                point.y = _map[-1].y
            elif not found and point.y > _map[-1].y:
                for element in _map:
                    if element.y < point.y:
                        element.y = point.y
            _map.append(point)
        self.map = _map

    def get_local_height(self, position):
        index = 0
        for j in range(len(self.map)):
            if self.map[j].x > position.x:
                index = j
                break
        if index == 0:
            return position.y - self.map[index].y
        k = (position.x - self.map[index-1].x) / (self.map[index].x - self.map[index-1].x)
        return position.y - (self.map[index].y - self.map[index-1].y) * k + self.map[index-1].y

    def get_local_flat_height(self, position):
        return position.y - self.flat_height

    def get_local_distances(self, position):
        distances = [self.flat_left - position.x, self.flat_right - position.x]
        distances.sort()
        return distances


class Turn:
    def __init__(self, rotation, thrust):
        self.rotation = rotation
        self.thrust = thrust

    def __str__(self):
        return '%s %s'.format([self.rotation, self.thrust])


class Planner:
    def __init__(self, position, speed, rotation, thrust):
        self.position = position
        self.speed = speed
        self.rotation = rotation
        self.thrust = thrust

    def get_turn(self, mars):
        local_height = mars.get_local_height(self.position)
        target_height = mars.get_local_flat_height(self.position)

        target_distances = mars.get_local_distances(self.position)

        return Turn(self.rotation, self.thrust)

    def get_landing_turn(self, rotation, thrust):
        if abs(rotation) <= MAX_ROTATION:
            _rotation = 0
        elif rotation > 0:
            _rotation = rotation - MAX_ROTATION
        else:
            _rotation = rotation + MAX_ROTATION

        _thrust = 0 if thrust <= 1 else thrust - 1

        return _rotation, _thrust

    def predict_fly(self, mars):
        _local_rotation, _local_thrust = self.get_landing_turn(self.rotation, self.thrust)
        _crush = False


def init():
    n = int(input())
    mars = Map()
    for i in range(n):
        land_x, land_y = [int(j) for j in input().split()]
        mars.add_point(Point(land_x, land_y))

    mars.finish_init()
    return mars


def make_turn(mars):
    # r: the rotation angle in degrees (-90 to 90).
    x, y, hs, vs, f, r, p = [int(i) for i in input().split()]
    planner = Planner(Point(x, y), Point(hs, vs), r, p)
    print(planner.get_turn(mars))


mars_map = init()
# game loop
while True:
    make_turn(mars_map)
