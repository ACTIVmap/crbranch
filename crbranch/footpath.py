

from enum import Enum
from .edge import Edge

class Footpath:

    class Side(Enum):
        LEFT = 0
        RIGHT = 1

    def __init__(self, side, nodes = []):
        self.__side = side
        self.__edges = [Edge(n1, n2) for n1, n2 in zip(nodes, nodes[1:])]

