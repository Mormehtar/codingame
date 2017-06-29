# https://www.codingame.com/ide/puzzle/platinum-rift-episode-2

import sys
import math
import random

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
    def __init__(self, zone_id, field):
        self.field = field
        self.id = zone_id
        self.visible = False
        self.platinum = 0
        self.owner = NEUTRAL
        self.links = []
        self.my_pods = 0
        self.enemy_pods = 0
        self.enemies_around = 0
        self.my_around = 0
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

    def after_turn(self):
        self.enemies_around = 0
        self.my_around = 0
        for link in self.links:
            self.enemies_around += link.enemy_pods
            self.my_around += link.my_pods


class BaseAttractor:
    def __init__(self, name, zone):
        self.name = name
        self.zone = zone
        self.value = -math.inf

    def stopper(self, zone):
        return False

    def expand(self, attractors=None):
        to_expand = {self} if attractors is None else set(attractors)
        while len(to_expand) > 0:
            new_expand = set()
            for attractor in to_expand:
                new_expand |= attractor.inner_expand()
            to_expand = new_expand

    def inner_expand(self):
        to_update = set()
        for zone in self.zone.links:
            if self.stopper(zone):
                continue
            attractor = zone.get_attractor(self.name)
            value = self.get_linked_attractor_value(zone)
            if attractor.value < value:
                attractor.value = value
                to_update.add(attractor)
        return to_update

    def get_linked_attractor_value(self, zone):
        return self.value - 1


class ReconAttractor(BaseAttractor):
    def get_linked_attractor_value(self, zone):
        return self.value - zone.enemies_around - 1

    def stopper(self, zone):
        return not zone.reconed


class EnemyAttractor(BaseAttractor):
    def get_linked_attractor_value(self, zone):
        return self.value - 1 + zone.platinum

    def stopper(self, zone):
        return zone.owner == zone.field.enemy


class Field:
    def __init__(self, zone_count, player_id):
        self.player = player_id
        self.enemy = 0 if player_id == 1 else 1
        self.zones = [Zone(z, self) for z in range(zone_count)]

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

    def after_turn(self):
        for zone in self.zones:
            zone.after_turn()


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
        to_update = set()
        for zone in self.field.enemy_pod_zones:
            if zone == self.enemy_hq:
                continue
            for link in zone.links:
                attractor = link.get_attractor('enemy_pods')
                attractor.value = max(
                    attractor.value,
                    zone.enemy_pods * self.enemy_pods_modifier + 1 + zone.platinum
                )
                to_update.add(attractor)
        if len(to_update) > 0:
            attractor = to_update.pop()
            to_update.add(attractor)
            attractor.expand(to_update)

    def build_recon_attractors(self):
        self.field.drop_attractor('recon')
        to_update = []
        for zone in self.field.zones:
            if zone.reconed:
                continue
            attractor = zone.get_attractor('recon')
            attractor.value = max(attractor.value, 0)
            to_update.append(attractor)
        if len(to_update) > 0:
            to_update[0].expand(to_update)

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
        self.field.after_turn()
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
        print(self.pods_to_move, file=sys.stderr)

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
            zone.links.sort(key=lambda x: x.platinum, reverse=True)
            for link in zone.links:
                if link.platinum == 0:
                    break
                if link.owner == self.field.player:
                    continue
                stack = min(pods_to_move, self.pods_to_move, 1)
                if stack > 0:
                    self.prepared_turn.make_turn(zone, link, stack)
                    self.pods_to_move -= stack
                    self.free_pods[zone.id] -= stack
                    pods_to_move = self.free_pods[zone.id]
                    reconing_pods += 1
                if pods_to_move <= 0:
                    break
        return reconing_pods

    def pods_recon(self, reconing_pods):
        print('pods_recon', file=sys.stderr)
        max_reconing_pods = max(
            self.field.my_pods // self.recon_part,
            -self.my_hq.get_attractor('enemy_menace').value
        )
        pods_to_move = min(max_reconing_pods - reconing_pods, self.pods_to_move)
        if pods_to_move <= 0:
            return
        reconing_structure = []
        for zone_id, _ in self.free_pods.items():
            reconing_structure.append(self.field.zones[zone_id])
        if len(reconing_structure) == 0:
            return
        reconing_structure.sort(
            key=lambda x: x.get_attractor('recon').value - x.get_attractor('enemy_menace').value,
            reverse=True
        )
        index = 0
        while pods_to_move > 0 and index < len(reconing_structure):
            zone = reconing_structure[index]
            value = zone.get_attractor('recon').value
            links = [z for z in zone.links if z.get_attractor('recon').value >= value]
            if len(links) == 0:
                continue
            links.sort(
                key=lambda x: x.get_attractor('recon').value,
                reverse=True
            )
            pods = self.free_pods[zone.id]

            if len(links) > pods:
                links = links[:pods]
                for link in links:
                    self.prepared_turn.make_turn(zone, link, 1)
                pods_to_move -= pods
                self.pods_to_move -= pods
                self.free_pods[zone.id] -= pods
            else:
                stack = pods // len(links)
                surplus = pods - stack * len(links)
                for link in links:
                    now_stack = stack
                    if surplus > 0:
                        now_stack += 1
                        surplus -= 1
                    pods -= now_stack
                    pods_to_move -= now_stack
                    self.pods_to_move -= now_stack
                    self.free_pods[zone.id] -= now_stack
                    self.prepared_turn.make_turn(zone, link, now_stack)

            index += 1

    def pods_push(self):
        print('pods_push', file=sys.stderr)
        pods_to_push = min(self.pods_to_move, self.field.my_pods // self.pushing_part)
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

    def cleanup_free_pods(self):
        print('cleanup_free_pods', file=sys.stderr)
        to_delete = []
        for zone_id, pods_to_move in self.free_pods.items():
            if pods_to_move <= 0:
                to_delete.append(zone_id)
        for zone_id in to_delete:
            del self.free_pods[zone_id]
        print(self.free_pods, file=sys.stderr)

    # def pods_attack(self):
    #     print('pods_attack', file=sys.stderr)
    #     print(self.pods_to_move, file=sys.stderr)
    #     if self.pods_to_move <= 0:
    #         return
    #     for zone_id, pods_to_move in self.free_pods.items():
    #         stack = pods_to_move
    #         self.pods_to_move -= stack
    #         del self.free_pods[zone_id]
    #         zone = self.field.zones[zone_id]
    #         zone.links.sort(key=lambda x: x.get_attractor('enemy_hq').value)
    #         self.prepared_turn.make_turn(zone, zone.links[-1], stack)

    def pods_attack(self):
        print('pods_attack', file=sys.stderr)
        print(self.pods_to_move, file=sys.stderr)
        if self.pods_to_move <= 0:
            return
        for zone_id, pods_to_move in self.free_pods.items():
            if pods_to_move >= self.pack_factor:
                stack = pods_to_move
                self.pods_to_move -= stack
                del self.free_pods[zone_id]
                zone = self.field.zones[zone_id]
                zone.links.sort(key=lambda x: x.get_attractor('enemy_hq').value)
                self.prepared_turn.make_turn(zone, zone.links[-1], stack)
        print(self.pods_to_move, file=sys.stderr)
        return self.build_pack()

    def build_pack(self):
        print('build_pack', file=sys.stderr)
        venues = []
        for zone_id, pods_to_move in self.free_pods.items():
            venues.append(self.field.zones[zone_id])
        if len(venues) <= 1:
            return
        venues.sort(key=lambda x: x.get_attractor('enemy_hq').value)
        venue = venues.pop()
        self.pods_to_move -= self.free_pods[venue.id]
        del self.free_pods[venue.id]

        self.field.drop_attractor('venue')
        venue.set_attractor('venue', 0)
        venue.get_attractor('venue').expand()
        for zone in venues:
            stack = self.free_pods[zone.id]
            self.free_pods[zone.id] = 0
            self.pods_to_move -= stack
            zone.links.sort(key=lambda x: x.get_attractor('venue').value, reverse=True)
            self.prepared_turn.make_turn(zone, zone.links[0], stack)

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
        for i in range(zone_count):
            strategy.new_turn_data(*[int(j) for j in input().split()])
        strategy.after_turn()
        print(strategy.build_turn())
        print("WAIT")


process()
