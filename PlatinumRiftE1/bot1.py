# https://www.codingame.com/ide/puzzle/platinum-rift-episode-1

import sys
import math
import random


class Zone:
    def __init__(self, zone_id, platinum):
        self.id = zone_id
        self.platinum = platinum
        self.owner = -1
        self.pods = [0] * 4
        self.links = []
        self.move_attractor = MoveAttractor()

    def link(self, zone):
        self.links.append(zone)

    def update(self, owner, pods):
        self.owner = owner
        self.pods = pods

    def set_attractor(self, attractor):
        self.move_attractor = attractor

    def get_pods_for_player(self, player):
        return self.pods[player]

    def get_pods_not_for_player(self, player):
        pods = 0
        for index in range(len(self.pods)):
            if index != player:
                pods += self.pods[index]
        return pods

    def get_linked_platinum(self):
        platinum = 0
        for zone in self.links:
            platinum += zone.platinum
        return platinum


class Move:
    def __init__(self, zone1, zone2, count):
        self.zone1 = zone1
        self.zone2 = zone2
        self.count = count

    def __str__(self):
        return '{} {} {}'.format(self.count, self.zone1.id, self.zone2.id)


class Purchase:
    def __init__(self, zone, count):
        self.zone = zone
        self.count = count

    def __str__(self):
        return '{} {}'.format(self.count, self.zone.id)


class Turn:
    WAIT = 'WAIT'

    def __init__(self):
        self.moves = []
        self.purchases = []

    def move(self, move):
        self.moves.append(move)

    def buy(self, purchase):
        self.purchases.append(purchase)

    def get_moves(self):
        if len(self.moves) == 0:
            return self.WAIT
        return ' '.join(map(lambda x: str(x), self.moves))

    def get_purchases(self):
        if len(self.purchases) == 0:
            return self.WAIT
        return ' '.join(map(lambda x: str(x), self.purchases))


class MoveAttractor:
    def __init__(self, value=-math.inf, interesting=False):
        self.value = value
        self.interesting = value != -math.inf

    def influence(self, attractor):
        new_value = attractor.value - 1
        if new_value > self.value:
            self.value = new_value
            return True
        return False

    def get_difference(self, attractor):
        return attractor.value - self.value

    def get_value(self):
        return self.value


class Strategy:
    foreign_platinum_weight = 6 * 20
    neutral_platinum_weight = 6 * 15
    neutral_points = 6
    enemy_points = 12

    max_deaths_in_turn = 3
    pod_price = 20

    def __init__(self, field_obj):
        self.field = field_obj

    def calc_potentials(self, zone):
        links = [z for z in zone.links if z.move_attractor.influence(zone.move_attractor)]
        for z in links:
            return self.calc_potentials(z)

    def recalculate_move_potentials(self):
        for zone in self.field.zones.values():
            attractor = self.get_move_attractor(zone)
            zone.set_attractor(attractor)
        for zone in self.field.zones.values():
            if zone.move_attractor.interesting:
                self.calc_potentials(zone)

    def calc_moves(self, turn):
        for zone in self.field.zones.values():
            my_pods = zone.pods[self.field.player]
            if my_pods > 0:
                priorities = []
                potential = -math.inf
                for link in zone.links:
                    dif = zone.move_attractor.get_difference(link.move_attractor) - link.pods[
                        self.field.player] + my_pods
                    if dif == potential:
                        priorities.append(link)
                    elif dif > potential and dif > 0:
                        priorities = [link]
                        potential = dif
                if len(priorities) == 0:
                    pass
                else:
                    stack = max(min(math.ceil(my_pods / len(priorities)), 3, potential), 1)
                    for z in priorities:
                        if my_pods > 0:
                            pack = min(stack, my_pods)
                            turn.move(Move(zone, z, pack))
                            my_pods -= pack

    def calc_purchases(self, turn):
        pods_to_by = self.field.platinum // self.pod_price
        print('pods_to_by', pods_to_by, file=sys.stderr)
        if pods_to_by <= 0:
            return
        easy_capture = []
        in_danger = []
        for zone in self.field.zones.values():
            if zone.owner == -1 and zone.platinum > 0:
                easy_capture.append(zone)
            elif zone.owner == self.field.player and zone.platinum > 0:
                enemies = 0
                for link in zone.links:
                    enemies += link.get_pods_not_for_player(self.field.player)
                if enemies > 0:
                    in_danger.append(zone)
        print('easy_capture', len(easy_capture), file=sys.stderr)
        print('in_danger', len(in_danger), file=sys.stderr)
        easy_capture.sort(key=lambda x: x.platinum + random.random(), reverse=True)
        in_danger.sort(key=lambda x: x.platinum + random.random(), reverse=True)
        while pods_to_by > 0 and len(easy_capture) + len(in_danger) > 0:
            if len(easy_capture) > 0 and (len(in_danger) == 0 or easy_capture[0].platinum > in_danger[0].platinum):
                zone = easy_capture.pop(0)
                stack = min(pods_to_by, self.max_deaths_in_turn, zone.platinum)
                if stack > 0:
                    turn.buy(Purchase(zone, stack))
                    pods_to_by -= stack
            else:
                zone = in_danger.pop(0)
                enemies = 0
                for link in zone.links:
                    enemies += link.get_pods_not_for_player(self.field.player)
                stack = min(pods_to_by, enemies, self.max_deaths_in_turn)
                if stack > 0:
                    turn.buy(Purchase(zone, stack))
                    pods_to_by -= stack
        if pods_to_by <= 0:
            return
        zones = [
            zone for zone in self.field.zones.values()
            if (zone.owner == -1 or zone.owner == self.field.player) and
               any(map(lambda x: x.owner != -1 and x.owner != self.field.player, zone.links))
        ]
        zones.sort(key=lambda x: x.move_attractor.get_value())
        while len(zones) > 0 and pods_to_by > 0:
            zone = zones.pop()
            stack = min(pods_to_by, self.max_deaths_in_turn)
            if stack > 0:
                turn.buy(Purchase(zone, stack))
                pods_to_by -= stack

    def get_move_attractor(self, zone):
        my_pods = 0
        enemy_pods = 0
        for index in range(len(zone.pods)):
            if index == self.field.player:
                my_pods = zone.pods[index]
            else:
                enemy_pods += zone.pods[index]

        if zone.platinum == 0:
            if zone.owner == -1:
                return MoveAttractor(self.neutral_points)
            if zone.owner != self.field.player:
                return MoveAttractor(self.enemy_points + enemy_pods)
            return MoveAttractor()
        if zone.owner == -1:
            return MoveAttractor(zone.platinum * self.neutral_platinum_weight + enemy_pods - my_pods)
        if zone.owner != self.field.player:
            return MoveAttractor(zone.platinum * self.foreign_platinum_weight + enemy_pods - my_pods)
        return MoveAttractor()


class Field:
    def __init__(self, player, zones_number):
        self.zones_number = zones_number
        self.zones = {}
        self.player = player
        self.platinum = 0

    def register_zone(self, zone_id, platinum):
        self.zones[zone_id] = Zone(zone_id, platinum)

    def make_link(self, id1, id2):
        zone1 = self.zones[id1]
        zone2 = self.zones[id2]
        zone1.link(zone2)
        zone2.link(zone1)

    def start_turn(self, platinum):
        self.platinum = platinum

    def update_zone(self, zone_id, owner, pods):
        self.zones[zone_id].update(owner, pods)


# player_count: the amount of players (2 to 4)
# my_id: my player ID (0, 1, 2 or 3)
# zone_count: the amount of zones on the map
# link_count: the amount of links between all zones
player_count, my_id, zone_count, link_count = [int(i) for i in input().split()]
field = Field(my_id, zone_count)
strategy = Strategy(field)
for i in range(zone_count):
    # zone_id: this zone's ID (between 0 and zoneCount-1)
    # platinum_source: the amount of Platinum this zone can provide per game turn
    field.register_zone(*[int(j) for j in input().split()])
for i in range(link_count):
    field.make_link(*[int(j) for j in input().split()])

# game loop
while True:
    field.start_turn(int(input()))  # my available Platinum
    for i in range(zone_count):
        # z_id: this zone's ID
        # owner_id: the player who owns this zone (-1 otherwise)
        # pods_p0: player 0's PODs on this zone
        # pods_p1: player 1's PODs on this zone
        # pods_p2: player 2's PODs on this zone (always 0 for a two player game)
        # pods_p3: player 3's PODs on this zone (always 0 for a two or three player game)
        z_id, zone_owner, *zone_pods = [int(j) for j in input().split()]
        field.update_zone(z_id, zone_owner, zone_pods)

    print('Renew field', file=sys.stderr)
    strategy.recalculate_move_potentials()
    print('recalculate move potentials', file=sys.stderr)
    turn = Turn()
    strategy.calc_moves(turn)
    print('calc moves', file=sys.stderr)
    strategy.calc_purchases(turn)
    print('calc purchases', file=sys.stderr)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)


    # first line for movement commands, second line for POD purchase (see the protocol in the statement for details)
    print(turn.get_moves())
    print(turn.get_purchases())
