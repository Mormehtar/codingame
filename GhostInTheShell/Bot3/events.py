class Event:
    def __init__(self, owner, eta):
        self.owner = owner
        self.eta = eta


class Troop(Event):
    def __init__(self, owner, cyborgs, eta):
        super().__init__(owner, eta)
        self.cyborgs = cyborgs


class Bomb(Event):
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
