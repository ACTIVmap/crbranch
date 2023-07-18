

from enum import Enum
from .edge import Edge

class Footpath:

    class Side(Enum):
        left = 0
        right = 1

    def __init__(self, side, edges = []):
        self.__edges = edges


    def load_example_001():
        # from 45.77349/3.09111 https://www.openstreetmap.org/way/931411095
        nodes = [21486411, 724112978, 4734568822, 8706544706, 566967069, 25891548, 21647182, 724111817]

        edges = [Edge(n1, n2) for n1, n2 in zip(nodes, nodes[1:])]

        return [Footpath(Footpath.Side.left, edges), Footpath(Footpath.Side.right, edges)]