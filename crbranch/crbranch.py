

from enum import Enum
import osmnx as ox
from shapely.geometry import Point
import geopandas as gp
import requests

import crmodel.crmodel as cm
import crmodel.config as cg
import crseg.segmentation as cs

from footpath import Footpath

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
        self.cr_model.computeModel(self.G, "data/intersection.json")


    def download_osm_data(self, filename, lng, lat, radius):
        p = Point(lng, lat)
        gdf_p = gp.GeoDataFrame(geometry=[p]).set_crs('EPSG:4326').to_crs('EPSG:3857')
        pb = gdf_p.buffer(distance=radius).envelope
        gdf_l = gp.GeoDataFrame(geometry=pb).to_crs('EPSG:4326')
        poly = gdf_l['geometry'][0]
        long1 = poly.exterior.coords.xy[0][0]
        long2 = poly.exterior.coords.xy[0][1]
        lat1 = poly.exterior.coords.xy[1][0]
        lat2 = poly.exterior.coords.xy[1][2]
        r = requests.get("https://www.openstreetmap.org/api/0.6/map?bbox=%s,%s,%s,%s"%(long1, lat1, long2, lat2), 
                        allow_redirects=True)
        if r.status_code != 200:
            print("Error from OpenStreetMap API. You should try using overpass.")
            return None

        open(filename, 'wb').write(r.content)    

    def load_data(self, lng = None, lat = None, osm_file = None, radius = 300):

        if osm_file:
            self.load_data_from_file(osm_file, lng, lat)
        else:
            tmp_file = "data/osm.osm"
            self.download_osm_data(tmp_file, lng, lat, radius)
            self.load_data_from_file(tmp_file, lng, lat)

    def add_branch(self, branch):
        # TODO
        pass


    def init_branch(self, o_branch):
        paths = []
        for way in o_branch.ways:
            if (way.sidewalks[0]):
                path = Footpath.extend_path(way.junctions[0], way.junctions[1], self.G, True)
                paths.append(Footpath(True, path))
            if (way.sidewalks[1]):
                path = Footpath.extend_path(way.junctions[0], way.junctions[1], self.G, False)
                paths.append(Footpath(False, path))

            if (way.island[0]):
                path = Footpath.extend_path(way.junctions[0], way.junctions[1], self.G, True)
                paths.append(Footpath(True, path, True))
        
        return paths

    def build_branches(self):

        self.branches = []

        for o_branch in self.cr_model.crossroad.branches:
            branch = self.init_branch(o_branch)
            self.add_branch(branch)

    def json_export(self, filename):
        # TODO
        pass