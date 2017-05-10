class Event:
    def __init__(self, owner, eta):
        self.owner = owner
        self.eta = eta


class Troop(Event):
    def __init__(self, owner, cyborgs, eta):
        super().__init__(owner, eta)
        self.cyborgs = cyborgs

    def get_modifier(self, core):
        return self.owner * core.owner * self.cyborgs


class Bomb(Event):
    @staticmethod
    def get_min_cyborgs_to_save_owner(node_core, modifier, number_of_bombs):
        pass


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

    def calculate_max_leave(self, node_core):
        # TODO Don't count bomb, not knowing where it will strike. Add functionality if think for enemy
        core = node_core.clone()
        max_leave = core.cyborgs
        core.cyborgs = 0
        last_turn = 0
        for turn in self.sorted_events:
            core.simulate_turns(turn - last_turn)
            bomb_events = 0
            modifier = 0
            for event in self.events[turn]:
                if isinstance(event, Bomb):
                    bomb_events += 1
                else:
                    modifier += event.get_modifier(core)
            core.cyborgs += modifier
            if core.cyborgs < 0:
                max_leave += core.cyborgs
                core.cyborgs = 0
            if max_leave <= 0:
                return 0
        return max_leave