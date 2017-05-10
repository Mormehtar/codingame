from GhostInTheShell.Bot3.constants import *


class State:
    def __init__(self):
        self.my_bombs = MAX_BOMBS
        self.enemy_bombs = MAX_BOMBS

        self._enemy_bombs_in_process = {}

    def track_enemy_bomb(self, source, eta):
        track_bomb = self._enemy_bombs_in_process.get(source)
        if track_bomb is None:
            self.enemy_bombs -= 1
            self._enemy_bombs_in_process[source] = [eta]
            return
        if eta not in track_bomb:
            self.enemy_bombs -= 1
            self._enemy_bombs_in_process[source].append(eta)

    def end_input(self):
        sources_to_delete = []
        for source, track_bomb in self._enemy_bombs_in_process:
            track_bomb = [eta-1 for eta in track_bomb if eta > 1]
            if len(track_bomb) == 0:
                sources_to_delete.append(source)
            else:
                self._enemy_bombs_in_process[source] = track_bomb
        for source_to_delete in sources_to_delete:
            del self._enemy_bombs_in_process[source_to_delete]

    def trigger_my_bomb(self):
        self.my_bombs -= 1
