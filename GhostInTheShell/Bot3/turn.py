WAIT_COMMAND = 'WAIT'
MOVE_COMMAND = 'MOVE'
BOMB_COMMAND = 'BOMB'
MESSAGE_COMMAND = 'MSG'


class TurnPlan:
    def __init__(self):
        self.turns = []

    def make_turn(self, turn):
        self.turns.append(turn)

    def __str__(self):
        if len(self.turns) == 0:
            self.turns.append(Wait())
        return '; '.join([str(i) for i in self.turns])


class Turn:
    def __init__(self):
        self.command = []

    def __str__(self):
        return ' '.join([str(i) for i in self.command])


class Move(Turn):
    def __init__(self, node1, node2, cyborgs):
        super().__init__()
        self.command = [MOVE_COMMAND, node1.id, node2.id, cyborgs]


class Wait(Turn):
    def __init__(self):
        super().__init__()
        self.command = [WAIT_COMMAND]
