from GhostInTheShell.Bot3.constants import *
import math


class Statistics:
    def __init__(self, nodes):
        self.nodes = nodes
        self.mean_distance = 0
        self.min_distance = math.inf
        self.max_distance = 0

        self._links = 0
        self._total_distance = 0

        self._min_distances = [[math.inf for _ in range(nodes)] for _ in range(nodes)]
        self._distances = [[math.inf for _ in range(nodes)] for _ in range(nodes)]

        self.nodes = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }

        self.production = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }

        self.cyborgs = {
            MY: 0,
            ENEMY: 0,
            NEUTRAL: 0
        }

    def add_link(self, node1_index, node2_index, distance):
        self._distances[node1_index][node2_index] = self._distances[node2_index][node1_index] = distance
        self._links += 1
        self._total_distance += distance
        self.min_distance = min(self.min_distance, distance)
        self.max_distance = max(self.max_distance, distance)

    def finish_init(self):
        self.mean_distance = self._total_distance / self._links
        self.build_min_distances()

    def build_min_distances(self):
        pass
