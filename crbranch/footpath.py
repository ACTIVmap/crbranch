

from enum import Enum
from .edge import Edge

from shapely import LineString, Polygon

class Footpath:

    class Side(Enum):
        LEFT = 0
        RIGHT = 1

    def __init__(self, side, nodes = [], is_island = False):
        self.__side = side
        self.__edges = [Edge(n1, n2) for n1, n2 in zip(nodes, nodes[1:])]
        self.is_island = is_island

    def build_island(self):
        # TODO
        return Polygon()

    def get_geometry(self):
        if len(self.__edges) == 0:
            return None

        if self.is_island:
            return self.build_island()
        else:
            return LineString([e.n1 for e in self.__edges] + [self.__edges[-1].n2])

