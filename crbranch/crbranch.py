

from enum import Enum
import osmnx as ox
import networkx as nx
from copy import deepcopy
from shapely.geometry import Point
import geopandas as gp
import requests
from xml.dom import minidom


import crmodel.crmodel as cm
import crmodel.config as cg
import crseg.segmentation as cs

from .footpath import Footpath
from .branch import Branch

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
        self.load_bounds(osm_file, self.G)
            
        # prepare network by removing unwanted ways
        self.G = cs.Segmentation.prepare_network(self.G)
        # build an undirected version of the graph
        self.undirected_G = ox.utils_graph.get_undirected(self.G)
        # segment it using topology and semantic
        seg = cs.Segmentation(self.undirected_G, C0 = self.C0, C1 = self.C1, C2 = self.C2, max_cycle_elements = self.max_cycle_elements)
        seg.process()
        seg.to_json("data/intersection.json", longitude, latitude)

        self.cr_model = cm.CrModel()
        self.cr_model.computeModel(self.G, "data/intersection.json")
        # set object list from model (inner region of the intersection)
        self.build_inner_region()

        # finally project on pseudo-mercator (only G)
        self.G = ox.projection.project_graph(self.G, to_crs="EPSG:3857")


    def load_bounds(self, osm_file, G):
        file = minidom.parse(osm_file)
        bounds = file.getElementsByTagName('bounds')
        minlat = float(bounds[0].attributes["minlat"].value)
        minlon = float(bounds[0].attributes["minlon"].value)
        maxlat = float(bounds[0].attributes["maxlat"].value)
        maxlon = float(bounds[0].attributes["maxlon"].value)
        nx.set_node_attributes(G, values=False, name="inbounds")
        for n in G.nodes:
            x = float(G.nodes[n]["x"])
            y = float(G.nodes[n]["y"])
            if x > minlon and x < maxlon and y > minlat and y < maxlat:
                G.nodes[n]["inbounds"] = True


    def build_inner_region(self):
        self.branch_edges = []
        for branch in self.cr_model.crossroad.branches:
            for way in branch.ways:
                self.branch_edges.append((way.junctions[0].id, way.junctions[1].id))

        self.inner_edges = []

        for way in self.cr_model.crossroad.ways.values():
            w = (way.junctions[0].id, way.junctions[1].id)
            if w not in self.branch_edges:
                self.inner_edges.append(w)


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
        self.branches.append(branch)
        # TODO: add other information along the branch


    def is_boundary_node(self, id):
        # if one adjacent edge is inside the intersection, return true
        for e in self.inner_edges:
            if e[0] == id or e[1] == id:
                return True
        # if one adjacent edge is not a branch, return false
        for n in self.undirected_G[id]:
            if (n, id) not in self.branch_edges and (id, n) not in self.branch_edges:
                return False
        # otherwise, it's a boundary node
        return True


    def init_branch(self, o_branch):
        paths = []
        for way in o_branch.ways:
            osm_n1 = way.junctions[0].id # first id in the OSM direction
            osm_n2 = way.junctions[1].id # last id in the OSM direction
            n1 = osm_n1 if self.is_boundary_node(osm_n1) else osm_n2
            n2 = osm_n2 if n1 == osm_n1 else osm_n1
            id_sidewalk = 0 if n1 == osm_n1 else 1
            if (way.sidewalks[id_sidewalk]):
                path = Footpath.extend_path(n1, n2, self.undirected_G, n1 == osm_n1)
                paths.append(Footpath(n1 == osm_n1, path))
            if (way.sidewalks[(id_sidewalk + 1) % 2]):
                path = Footpath.extend_path(n1, n2, self.undirected_G, n1 != osm_n1)
                paths.append(Footpath(n1 != osm_n1, path))
            if (way.islands[id_sidewalk]):
                path = [n1, n2]
                paths.append(Footpath(n1 == osm_n1, path, True))
        
        # TODO: add missing islands
        # identify the list of open edges (edges that are only in one existing path)

        return Branch(paths)

    def build_branches(self):

        self.branches = []

        for o_branch in self.cr_model.crossroad.branches:
            branch = self.init_branch(o_branch)
            self.add_branch(branch)

    def json_export(self, filename):
        # TODO
        pass

    def geojson_export(self, filename):
        lines = []
        sides = []
        is_island = []

        for b in self.branches:
            for p in b.footpaths:
                lines.append(p.get_geometry(self.undirected_G))
                sides.append(p.side)
                is_island.append(p.is_island)
        
        gdr = gp.GeoDataFrame({'side': sides, 'is_island': is_island, 'geometry': lines})
        gdr.to_file(filename)
