# https://www.codingame.com/ide/puzzle/platinum-rift-episode-2

import sys
import math

# **************************************************************************************************************
NEUTRAL = -1
MY = 1
ENEMY = 2

MAX_DEATH = 3

BOT_PRICE = 20


class AttractorFactory:
    @classmethod
    def get_attractor(cls, name, zone):
        if name == 'recon':
            return ReconAttractor(name, zone)
        if name == 'enemy_pods':
            return EnemyAttractor(name, zone)
        return BaseAttractor(name, zone)


class Zone:
    def __init__(self, zone_id):
        self.id = zone_id
        self.visible = False
        self.platinum = 0
        self.owner = NEUTRAL
        self.links = []
        self.my_pods = 0
        self.enemy_pods = 0
        self.attractors = {}
        self.reconed = False

    def get_attractor(self, name):
        attractor = self.attractors.get(name)
        if attractor is None:
            self.attractors[name] = attractor = AttractorFactory.get_attractor(name, self)
        return attractor

    def link(self, zone):
        self.links.append(zone)

    def update(self, owner_id, my_pods, enemy_pods, visible, platinum):
        self.my_pods = my_pods
        self.visible = visible
        if visible:
            self.reconed = True
            self.owner = owner_id
            self.enemy_pods = enemy_pods
            self.platinum = platinum

    def drop_attractor(self, name):
        if self.attractors.get(name) is None:
            return
        del self.attractors[name]


class BaseAttractor:
    def __init__(self, name, zone):
        self.name = name
        self.zone = zone
        self.value = -math.inf

    def expand(self):
        to_update = []
        for zone in self.zone.links:
            value = self.get_linked_attractor_value(zone)
            attractor = zone.get_attractor(self.name)
            if attractor.value < value:
                attractor.value = value
                to_update.append(attractor)
        for attractor in to_update:
            attractor.expand()

    def get_linked_attractor_value(self, zone):
        return self.value - 1


class ReconAttractor(BaseAttractor):
    def get_linked_attractor_value(self, zone):
        pods = zone.my_pods
        for link in zone.links:
            pods += link.my_pods
        return self.value - pods - 1


class EnemyAttractor(BaseAttractor):
    def get_linked_attractor_value(self, zone):
        return self.value - 1 + zone.platinum


class Field:
    def __init__(self, zone_count, player_id):
        self.player = player_id
        self.zones = [Zone(z) for z in range(zone_count)]

        self.my_pod_zones = []
        self.enemy_pod_zones = []

        self.my_platinum_fields = []
        self.enemy_platinum_fields = []
        self.neutral_platinum_fields = []

        self.my_fields = 0
        self.enemy_fields = 0
        self.neutral_fields = 0

        self.platinum = 0

        self.my_pods = 0
        self.enemy_pods = 0

    def drop_attractor(self, name):
        for zone in self.zones:
            zone.drop_attractor(name)

    def link(self, zone_id1, zone_id2):
        zone1 = self.zones[zone_id1]
        zone2 = self.zones[zone_id2]
        zone1.link(zone2)
        zone2.link(zone1)

    def update(self, zone_id, owner_id, pods_p0, pods_p1, visible, platinum):
        zone = self.zones[zone_id]
        my_pods, enemy_pods = [pods_p0, pods_p1] if self.player == 0 else [pods_p1, pods_p0]
        if owner_id == NEUTRAL:
            if zone.platinum > 0 or platinum > 0:
                self.neutral_platinum_fields.append(zone)
            self.neutral_fields += 1
        elif owner_id == self.player:
            if zone.platinum > 0 or platinum > 0:
                self.my_platinum_fields.append(zone)
            self.my_fields += 1
        else:
            if zone.platinum > 0 or platinum > 0:
                self.enemy_platinum_fields.append(zone)
            self.enemy_fields += 1

        self.my_pods += my_pods
        self.enemy_pods += enemy_pods

        if my_pods > 0:
            self.my_pod_zones.append(zone)
        if enemy_pods > 0:
            self.enemy_pod_zones.append(zone)

        zone.update(owner_id, my_pods, enemy_pods, visible, platinum)

    def new_turn(self, platinum):
        self.platinum = platinum
        self.my_pod_zones = []
        self.enemy_pod_zones = []

        self.my_platinum_fields = []
        self.enemy_platinum_fields = []
        self.neutral_platinum_fields = []

        self.my_fields = 0
        self.enemy_fields = 0
        self.neutral_fields = 0


class Turn:
    def __init__(self):
        self.turns = []

    def __str__(self):
        if len(self.turns) == 0:
            return "WAIT"
        else:
            return " ".join(self.turns)

    def make_turn(self, zone1, zone2, count):
        self.turns.append("{} {} {}".format(count, zone1.id, zone2.id))


class Strategy:

    recon_modifier = 20
    recon_part = 10
    pushing_part = 2
    enemy_pods_modifier = 7
    pods_overcome_modifier = 2

    pack_factor = MAX_DEATH + 1

    def __init__(self, player_id, zone_count):
        self.field = Field(zone_count, player_id)
        self.my_hq = None
        self.enemy_hq = None
        self.prepared_turn = Turn()

        self.turn = 0
        self.pods_to_move = 0

        self.free_pods = {}

    def new_turn_data(self, zone_id, owner_id, pods_p0, pods_p1, visible, platinum):
        if self.turn == 0:
            if owner_id == self.field.player:
                self.my_hq = self.field.zones[zone_id]
            elif owner_id != NEUTRAL:
                self.enemy_hq = self.field.zones[zone_id]

        self.field.update(zone_id, owner_id, pods_p0, pods_p1, visible, platinum)

    def link(self, zone_id1, zone_id2):
        return self.field.link(zone_id1, zone_id2)

    def new_turn(self, platinum):
        self.field.new_turn(platinum)

    def build_my_hq_attractors(self):
        hq_attractor = self.my_hq.get_attractor('my_hq')
        hq_attractor.value = 0
        hq_attractor.expand()

    def build_enemy_hq_attractors(self):
        hq_attractor = self.enemy_hq.get_attractor('enemy_hq')
        hq_attractor.value = 0
        hq_attractor.expand()

    def build_enemy_attractors(self):
        self.field.drop_attractor('enemy_pods')
        to_update = []
        for zone in self.field.enemy_pod_zones:
            for link in zone.links:
                attractor = link.get_attractor('enemy_pods')
                attractor.value = max(
                    attractor.value,
                    zone.enemy_pods * self.enemy_pods_modifier + 1 + zone.platinum
                )
                to_update.append(link)
        for zone in self.field.enemy_pod_zones:
            zone.get_attractor('enemy_pods').expand()

    def build_recon_attractors(self):
        self.field.drop_attractor('recon')
        to_update = []
        for zone in self.field.zones:
            if zone.reconed:
                continue
            attractor = zone.get_attractor('recon')
            attractor.value = max(attractor.value, 0)
            to_update.append(zone)
        for zone in to_update:
            zone.get_attractor('recon').expand()

    def build_enemy_menace_attractors(self):
        self.field.drop_attractor('enemy_menace')
        to_update = []
        for zone in self.field.zones:
            if zone.owner == NEUTRAL or zone.owner == self.field.player:
                continue
            attractor = zone.get_attractor('enemy_menace')
            attractor.value = max(attractor.value, 0)
            to_update.append(zone)
        for zone in to_update:
            zone.get_attractor('enemy_menace').expand()

    def after_first_turn(self):
        self.build_my_hq_attractors()
        self.build_enemy_hq_attractors()

    def after_other_turns(self):
        pass

    def renew_potentials(self):
        print('build_enemy_attractors', file=sys.stderr)
        self.build_enemy_attractors()
        print('build_enemy_menace_attractors', file=sys.stderr)
        self.build_enemy_menace_attractors()
        print('build_recon_attractors', file=sys.stderr)
        self.build_recon_attractors()
        print('renew_potentials finished', file=sys.stderr)

    def after_turn(self):
        print('after_turn', file=sys.stderr)
        if self.turn == 0:
            print('after_first_turn', file=sys.stderr)
            self.after_first_turn()
        print('renew_potentials', file=sys.stderr)
        self.renew_potentials()
        print('after_turn finished', file=sys.stderr)
        self.turn += 1

    def build_free_pods(self):
        print('build_free_pods', file=sys.stderr)
        self.pods_to_move = self.field.my_pods
        self.free_pods = {}
        for zone in self.field.my_pod_zones:
            self.free_pods[zone.id] = zone.my_pods
        print(self.pods_to_move, self.free_pods, file=sys.stderr)

    def send_pods_to_stop_enemy(self):
        print('send_pods_to_stop_enemy', file=sys.stderr)
        max_defending_pods = (self.field.enemy_pods - self.enemy_hq.enemy_pods) * self.pods_overcome_modifier
        defending_pods = 0
        if max_defending_pods <= 0 or self.pods_to_move <= 0:
            return
        defending_zones = []
        for zone_id, pods_to_move in self.free_pods.items():
            defending_zones.append(self.field.zones[zone_id])
        print(max_defending_pods, len(defending_zones), file=sys.stderr)
        defending_zones.sort(key=lambda x: x.get_attractor('enemy_pods').value + x.get_attractor('my_hq').value)
        while len(defending_zones) > 0 and defending_pods < max_defending_pods and self.pods_to_move > 0:
            zone = defending_zones.pop()
            zone.links.sort(key=lambda x: x.get_attractor('enemy_pods').value, reverse=True)
            for link in zone.links:
                if link.get_attractor('enemy_pods').value > zone.get_attractor('enemy_pods').value:
                    stack = min(self.pods_overcome_modifier, self.pods_to_move, self.free_pods[zone.id])
                    self.pods_to_move -= stack
                    self.free_pods[zone.id] -= stack
                    self.prepared_turn.make_turn(zone, link, stack)
                elif link.get_attractor('enemy_pods').value == zone.get_attractor('enemy_pods').value:
                    stack = min(self.pods_overcome_modifier, self.pods_to_move, self.free_pods[zone.id])
                    self.pods_to_move -= stack
                    self.free_pods[zone.id] -= stack
                else:
                    break
                if self.free_pods[zone.id] <= 0:
                    break
            if self.free_pods[zone.id] <= 0:
                del self.free_pods[zone.id]

    def pods_look_around(self):
        print('pods_look_around', file=sys.stderr)
        reconing_pods = 0
        for zone_id, pods_to_move in self.free_pods.items():
            zone = self.field.zones[zone_id]
            zone.links.sort(key=lambda x: x.platinum and x.owner != self.field.player, reverse=True)
            for link in zone.links:
                if link.platinum == 0:
                    break
                stack = min(pods_to_move, self.pods_to_move, 1)
                if stack > 0:
                    self.prepared_turn.make_turn(zone, link, stack)
                    self.pods_to_move -= stack
                    self.free_pods[zone.id] -= stack
                    pods_to_move = self.free_pods[zone.id]
                    reconing_pods += 1
                if pods_to_move <= 0:
                    break
        print(reconing_pods, self.pods_to_move, file=sys.stderr)
        return reconing_pods

    def pods_recon(self, reconing_pods):
        print('pods_recon', file=sys.stderr)
        print(self.field.my_pods, self.recon_part, self.my_hq.get_attractor('enemy_menace').value, file=sys.stderr)
        max_reconing_pods = max(
            self.field.my_pods // self.recon_part,
            -self.my_hq.get_attractor('enemy_menace').value
        )
        pods_to_move = min(max_reconing_pods - reconing_pods, self.pods_to_move)
        print(reconing_pods, max_reconing_pods, pods_to_move, self.pods_to_move, file=sys.stderr)
        if pods_to_move <= 0:
            return
        reconing_structure = []
        for zone_id, pods_to_move in self.free_pods.items():
            reconing_structure.append(self.field.zones[zone_id])
        if len(reconing_structure) == 0:
            return
        reconing_structure.sort(
            key=lambda x: x.get_attractor('recon').value - x.get_attractor('enemy_menace').value,
            reverse=True
        )
        index = 0
        while pods_to_move > 0:
            zone = reconing_structure[index]
            zone.links.sort(
                key=lambda x: x.get_attractor('recon').value - x.get_attractor('enemy_menace').value,
                reverse=True
            )
            pods = self.free_pods[zone.id]
            for link in zone.links:
                if pods <= 0 or pods_to_move <= 0:
                    break
                stack = 1
                pods -= stack
                pods_to_move -= stack
                self.pods_to_move -= stack
                self.prepared_turn.make_turn(zone, link, stack)
            self.free_pods[zone.id] = pods
            index = (index + 1) % len(reconing_structure)
        print(reconing_pods, max_reconing_pods, pods_to_move, self.pods_to_move, file=sys.stderr)

    def pods_push(self):
        print('pods_push', file=sys.stderr)
        pods_to_push = min(self.pods_to_move, self.field.my_pods // self.pushing_part)
        print(pods_to_push, self.pods_to_move, file=sys.stderr)
        if pods_to_push <= 0:
            return
        pushing_structure = []
        for zone_id, pods_to_move in self.free_pods.items():
            pushing_structure.append(self.field.zones[zone_id])
        if len(pushing_structure) == 0:
            return
        pushing_structure.sort(
            key=lambda x: x.get_attractor('enemy_menace').value - x.get_attractor('enemy_pods').value,
            reverse=True
        )
        index = 0

        while pods_to_push > 0 and self.pods_to_move > 0:
            zone = pushing_structure[index]
            if self.free_pods[zone.id] <= 0:
                continue
            zone.links.sort(key=lambda x: x.get_attractor('enemy_menace').value)
            for link in zone.links:
                if self.free_pods[zone.id] <= 0 or pods_to_push <= 0:
                    break
                if link.get_attractor('enemy_menace').value > zone.get_attractor('enemy_menace').value:
                    self.prepared_turn.make_turn(zone, link, 1)
                    self.free_pods[zone.id] -= 1
                    self.pods_to_move -= 1
                    pods_to_push -= 1
            index = (index + 1) % len(pushing_structure)
        print(pods_to_push, self.pods_to_move, file=sys.stderr)

    def cleanup_free_pods(self):
        print('cleanup_free_pods', file=sys.stderr)
        to_delete = []
        for zone_id, pods_to_move in self.free_pods.items():
            if pods_to_move <= 0:
                to_delete.append(zone_id)
        for zone_id in to_delete:
            del self.free_pods[zone_id]
        print(self.free_pods, file=sys.stderr)

    def pods_attack(self):
        print('pods_attack', file=sys.stderr)
        print(self.pods_to_move, file=sys.stderr)
        if self.pods_to_move <= 0:
            return
        for zone_id, pods_to_move in self.free_pods.items():
            stack = pods_to_move
            self.pods_to_move -= stack
            del self.free_pods[zone_id]
            zone = self.field.zones[zone_id]
            zone.links.sort(key=lambda x: x.get_attractor('enemy_hq').value)
            self.prepared_turn.make_turn(zone, zone.links[-1], stack)

    # def pods_attack(self):
    #     print('pods_attack', file=sys.stderr)
    #     print(self.pods_to_move, file=sys.stderr)
    #     if self.pods_to_move <= 0:
    #         return
    #     for zone_id, pods_to_move in self.free_pods.items():
    #         if pods_to_move >= self.pack_factor:
    #             stack = pods_to_move
    #             self.pods_to_move -= stack
    #             del self.free_pods[zone_id]
    #             zone = self.field.zones[zone_id]
    #             zone.links.sort(key=lambda x: x.get_attractor('enemy_hq').value)
    #             self.prepared_turn.make_turn(zone, zone.links[-1], stack)
    #     print(self.pods_to_move, file=sys.stderr)
    #     return self.build_pack()

    # def build_pack(self):
    #     print('build_pack', file=sys.stderr)
    #     venues = []
    #     for zone_id, pods_to_move in self.free_pods.items():
    #         venues.append(self.field.zones[zone_id])
    #     print(len(venues), self.pods_to_move, file=sys.stderr)
    #     if len(venues) <= 1:
    #         return
    #     venues.sort(key=lambda x: x.get_attractor('enemy_hq').value)
    #     venue = venues.pop()
    #     wait_for = self.pack_factor - self.free_pods[venue.id]
    #     self.pods_to_move -= self.free_pods[venue.id]
    #     del self.free_pods[venue.id]
    #
    #     self.field.drop_attractor('venue')
    #     venue.set_attractor('venue', 0)
    #     venue.get_attractor('venue').expand()
    #     venues.sort(key=lambda x: x.get_attractor('venue').value)
    #     while wait_for > 0 and len(venues):
    #         zone = venues.pop()
    #         stack = min(wait_for, self.free_pods[zone.id])
    #         self.free_pods[zone.id] -= stack
    #         if self.free_pods[zone.id] == 0:
    #             del self.free_pods[zone.id]
    #         self.pods_to_move -= stack
    #         wait_for -= stack
    #     print(len(venues), self.pods_to_move, file=sys.stderr)
    #     if len(venues) > 1:
    #         return self.build_pack()

    def build_turn(self):
        self.prepared_turn = Turn()

        self.build_free_pods()
        reconing_pods = self.pods_look_around()
        if self.pods_to_move <= 0:
            return self.prepared_turn
        self.cleanup_free_pods()
        self.pods_recon(reconing_pods)
        if self.pods_to_move <= 0:
            return self.prepared_turn
        self.cleanup_free_pods()
        self.pods_push()
        if self.pods_to_move <= 0:
            return self.prepared_turn
        self.cleanup_free_pods()
        self.send_pods_to_stop_enemy()
        if self.pods_to_move <= 0:
            return self.prepared_turn
        self.cleanup_free_pods()
        self.pods_attack()

        print('prepared_turn', self.prepared_turn, file=sys.stderr)
        return self.prepared_turn


# **************************************************************************************************************

def process():
    _, my_id, zone_count, link_count = [int(i) for i in input().split()]
    strategy = Strategy(my_id, zone_count)
    for i in range(zone_count):
        input()
    for i in range(link_count):
        strategy.link(*[int(j) for j in input().split()])

    # game loop
    while True:
        strategy.new_turn(int(input()))
        print('new_turn', file=sys.stderr)

        for i in range(zone_count):
            print('new_turn_data', file=sys.stderr)
            strategy.new_turn_data(*[int(j) for j in input().split()])

        print('new_turn_data finished', file=sys.stderr)
        strategy.after_turn()
        print('after_turn', file=sys.stderr)

        print(strategy.build_turn())
        print("WAIT")

process()
