
from .footpath import Footpath



class Branch:

    def __init__(self, footpaths = []):
        self.footpaths = footpaths

    def load_example_001():
        # from 45.77349/3.09111 https://www.openstreetmap.org/way/931411095
        nodes = [21486411, 724112978, 4734568822, 8706544706, 566967069, 25891548, 21647182, 724111817]

        return Branch([Footpath(Footpath.Side.LEFT, nodes), Footpath(Footpath.Side.RIGHT, nodes)])