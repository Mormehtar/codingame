from GhostInTheShell.Bot3.constants import *


class Event:
    def __init__(self, owner, eta):
        self.owner = owner
        self.eta = eta
        self.priority = 0

    def get_modifier(self, core):
        return 0

    def emulate_event(self, core):
        pass


class Troop(Event):
    def __init__(self, owner, cyborgs, eta):
        super().__init__(owner, eta)
        self.cyborgs = cyborgs
        self.priority = 1000

    def get_modifier(self, core):
        return self.owner * core.owner * self.cyborgs

    def emulate_event(self, core):
        core.modifier[self.owner] += self.cyborgs


class Bomb(Event):
    def __init__(self, owner, eta):
        super().__init__(owner, eta)
        self.priority = 900

    def emulate_event(self, core):
        core.cyborgs -= min(max(BOMB_MINIMAL_CASUALTY, core.cyborgs // BOMB_MULTIPLIER), core.cyborgs)
        core.repairing = BOMB_REPAIRING


class Events:
    def __init__(self):
        self.event_turns = set()
        self.sorted_events = []
        self.events = {}

    def add_event(self, event):
        self.event_turns.add(event.eta)
        if self.events.get(event.eta) is None:
            self.events[event.eta] = []
        self.events[event.eta].append(event)

    def end_input(self):
        self.sorted_events = list(self.event_turns)
        self.sorted_events.sort()
        for turn in self.sorted_events:
            self.events[turn].sort(lambda x: x.priority)

    def calculate_max_leave(self, node_core):
        # TODO Don't count bomb, not knowing where it will strike. Add functionality if think for enemy
        core = node_core.clone()
        max_leave = core.cyborgs
        core.cyborgs = 0
        last_turn = 0
        for turn in self.sorted_events:
            core.simulate_turns(turn - last_turn)
            modifier = 0
            for event in self.events[turn]:
                modifier += event.get_modifier(core)
            core.cyborgs += modifier
            if core.cyborgs < 0:
                max_leave += core.cyborgs
                core.cyborgs = 0
            if max_leave <= 0:
                return 0
            last_turn = turn
        return max_leave

    def calculate_state_on_distance(self, node_core, distance):
        core = node_core.clone()
        last_turn = 0
        for turn in self.sorted_events:
            if turn >= distance:
                break
            core.simulate_turns(turn - last_turn)
            for event in self.events[turn]:
                event.emulate_event(core)
            core.use_modifier()
            last_turn = turn
        if last_turn < distance:
            core.simulate_turns(distance - last_turn)
        return core
