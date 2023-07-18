

from enum import Enum
from .edge import Edge

from shapely import LineString, Polygon

class Footpath:

    class Side(Enum):
        LEFT = 0
        RIGHT = 1


    def __init__(self, side, nodes = [], is_island = False):
        self.side = side
        self.edges = [Edge(n1, n2) for n1, n2 in zip(nodes, nodes[1:])]
        self.is_island = is_island


    def build_island(self):
        # TODO
        return Polygon()


    def get_osm_node_ids(self, G):
        return [e.n1 for e in self.edges] + [self.edges[-1].n2]


    def get_osm_nodes(self, G):
        return [G.nodes[n] for n in self.get_osm_node_ids(G)]
        

    def get_geometry(self, G):
        if len(self.edges) == 0:
            return None

        if self.is_island:
            return self.build_island()
        else:
            return LineString([(n["x"], n["y"]) for n in self.get_osm_nodes(G)])


    def extend_path(n1, n2, G):
        return [n1, n2]
