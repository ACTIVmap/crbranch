

from enum import Enum
import osmnx as ox

import crmodel.crmodel as cm
import crmodel.config as cg
import crseg.segmentation as cs

class CrBranch:

    class NetworkStructure(Enum):
        ONLY_CROSSINGS = 0
        FULL_CONNECTIVITY = 1

    class LevelOfDetails(Enum):
        BASIC = 0
        DETAILLED = 1

    def __init__(self, 
                lod = LevelOfDetails.BASIC, network_structure = NetworkStructure.ONLY_CROSSINGS,
                C0 = 2, C1 = 2, C2 = 4, max_cycle_elements = 10):
        self.lod = lod
        self.network_structure = network_structure

        self.C0 = C0
        self.C1 = C1
        self.C2 = C2
        self.max_cycle_elements = max_cycle_elements

    def load_data_from_file(self, osm_file, longitude, latitude):
        # load in geopandas for amenities & co
        self.osm_data = ox.features.features_from_xml(osm_file)

        # build model via crmodel
        ox.settings.useful_tags_way = ox.settings.useful_tags_way + cg.way_tags_to_keep
        ox.settings.useful_tags_node = ox.settings.useful_tags_way + cg.node_tags_to_keep
        self.G = ox.graph_from_xml(osm_file, simplify=False, retain_all=True)

        # prepae network by removing unwanted ways
        self.G = cs.Segmentation.prepare_network(self.G)
        # build an undirected version of the graph
        self.undirected_G = ox.utils_graph.get_undirected(self.G)
        # segment it using topology and semantic
        seg = cs.Segmentation(self.undirected_G, C0 = self.C0, C1 = self.C1, C2 = self.C2, max_cycle_elements = self.max_cycle_elements)
        seg.process()
        seg.to_json("data/intersection.json", longitude, latitude)

        self.cr_model = cm.CrModel()
        self.cr_model.computeModel(G, "data/intersection.json")


    def load_data(self, lng = None, lat = None, osm_file = None):

        if osm_file:
            self.load_data_from_file(osm_file, lng, lat)
        else:
            # TODO: download osm file
            #tmp_file = ???
            #self.load_data_from_file(tmp_file)
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