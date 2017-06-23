
class Zone:
    def __init__(self, zone_id, platinum):
        self.id = zone_id
        self.platinum = platinum
        self.links = []
        self.owner = -1
        self.pods = [0]*4

    def link(self, zone):
        self.links.append(zone)

    def update(self, owner, pods):
        self.owner = owner
        self.pods = pods


class Field:
    def __init__(self, player_id, zone_count):
        self.zones = {}
        self.zone_count = zone_count
        self.player = player_id
        self.platinum = 0

    def add_zone(self, zone):
        self.zones[zone.id] = zone

    def link(self, zone_id1, zone_id2):
        zone1 = self.zones[zone_id1]
        zone2 = self.zones[zone_id2]
        zone1.link(zone2)
        zone2.link(zone1)

    def finish_init(self):
        pass

    def start_turn(self, platinum):
        self.platinum = platinum

    def get_zone(self, zone_id):
        return self.zones[zone_id]


class Strategy:
    def __init__(self, field):
        self.field = field

    def prepare(self):
        pass

    def build_move(self):
        turn = Turn()
        return turn


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


def process_init():
    player_count, my_id, zone_count, link_count = [int(i) for i in input().split()]
    field = Field(my_id, zone_count)
    for i in range(zone_count):
        field.add_zone(Zone(*[int(j) for j in input().split()]))
    for i in range(link_count):
        field.link(*[int(j) for j in input().split()])
    field.finish_init()
    return field


def process_turn(strategy):
    strategy.field.start_turn(int(input()))
    for i in range(strategy.field.zone_count):
        z_id, zone_owner, *zone_pods = [int(j) for j in input().split()]
        zone = strategy.field.get_zone(z_id)
        zone.update(zone_owner, zone_pods)
    strategy.prepare()
    move = strategy.build_move()
    print(move.get_moves())
    print(move.get_purchases())


def pocess_main_loop(strategy):
    while True:
        process_turn(strategy)


pocess_main_loop(Strategy(process_init()))
