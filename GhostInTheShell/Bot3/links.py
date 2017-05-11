class Link:
    def __init__(self, node, distance):
        self.node = node
        self.distance = distance


class Links:
    def __init__(self, node):
        self.node = node
        self.links = []

    def add_link(self, node, distance):
        self.links.append(Link(node, distance))

    def get_neighbours(self):
        return map(lambda link: link.node, self.links)
