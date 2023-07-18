

from enum import Enum

class CrBranch:

    class NetworkStructure(Enum):
        ONLY_CROSSINGS = 0
        FULL_CONNECTIVITY = 1

    class LevelOfDetails(Enum):
        BASIC = 0
        DETAILLED = 1

    def __init__(self, lod = LevelOfDetails.BASIC, network_structure = NetworkStructure.ONLY_CROSSINGS):
        self.lod = lod
        self.network_structure = network_structure


    def load_data(self, lng = None, lat = None, osm_file = None):
        # TODO
        pass

    def build_branch(self, branch):
        # TODO
        pass

    def build_branches(self):
        # TODO
        # for branch_paths in :
        #    self.build_branch(branch_paths)
        pass

    def json_export(self, filename):
        # TODO
        pass