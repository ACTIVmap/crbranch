import osmnx as ox

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


    def get_osm_node_ids(self):
        return [e.n1 for e in self.edges] + [self.edges[-1].n2]


    def get_osm_nodes(self, G):
        return [G.nodes[n] for n in self.get_osm_node_ids()]
        

    def get_geometry(self, G):
        if len(self.edges) == 0:
            return None

        if self.is_island:
            return self.build_island()
        else:
            return LineString([(n["x"], n["y"]) for n in self.get_osm_nodes(G)])


    def is_turn(G, m, c1, c2):
        ta = Footpath.turn_angle(G, m, c1, c2)
        return ta < 90 or ta > 90 * 3


    def is_similar_edge(G, e1, e2):
        if e1[1] not in G[e1[0]] or e2[1] not in G[e2[0]]:
            return False

        tags_e1 = G[e1[0]][e1[1]][0]
        tags_e2 = G[e2[0]][e2[1]][0]

        if not "name" in tags_e1 or not "name" in tags_e2:
            return False
        if tags_e1["name"] != tags_e2["name"]:
            return False
        if Footpath.is_turn(G, e1[1], e1[0], e2[1]):
            return False
        return True


    def turn_angle(G, middle, n2, n3):
        c1 = (G.nodes[middle]["x"], G.nodes[middle]["y"])
        c2 = (G.nodes[n2]["x"], G.nodes[n2]["y"])
        c3 = (G.nodes[n3]["x"], G.nodes[n3]["y"])
        b1 = ox.bearing.calculate_bearing(c2[1], c2[0], c1[1], c1[0])
        b2 = ox.bearing.calculate_bearing(c3[1], c3[0], c1[1], c1[0])
        a = b2 - b1
        if a < 0:
            a += 360
        return a

    def find_next_edge(G, n1, n2, side):
        other = [n for n in G[n2] if n != n1 and Footpath.is_similar_edge(G, [n1, n2], [n2, n])]
        if len(other) == 0:
            return None
        elif len(other) == 1:
            return other[0]
        else:
            sorted_other = sorted(other, key=lambda n: Footpath.turn_angle(G, n2, n1, n), reverse=not side)
            return sorted_other[0]

    
    def extend_path(n1, n2, G, side):
        next = Footpath.find_next_edge(G, n1, n2, side)
        # if not found, we reach the end of the path
        if next is None:
            return [n1, n2]
        else:
            # if found, we propagate the extension
            return [n1] + Footpath.extend_path(n2, next, G, side)
