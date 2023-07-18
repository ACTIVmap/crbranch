#!/usr/bin/env python3
#encoding: utf-8

from crbranch.branch import Branch
from crbranch.crbranch import CrBranch
from crbranch.footpath import Footpath

crbranch = CrBranch()
crbranch.load_data(osm_file = "data/example_clermont_18_07_2023.osm", lat=45.77349, lng=3.09111)

nodes = [21486411, 724112978, 4734568822, 8706544706, 566967069, 25891548, 21647182, 724111817]

branch = Branch([Footpath(Footpath.Side.LEFT, nodes), Footpath(Footpath.Side.RIGHT, nodes)])

crbranch.build_branch(branch)

crbranch.json_export("/tmp/out.json")
