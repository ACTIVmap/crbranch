#!/usr/bin/env python3
#encoding: utf-8

from crbranch.branch import Branch
from crbranch.crbranch import CrBranch
from crbranch.footpath import Footpath

crbranch = CrBranch()
#crbranch.load_data(lat=45.77355, lng=3.08992)
crbranch.load_data(lat=43.60580, lng=1.44874)

crbranch.build_branches()

crbranch.geojson_export("/tmp/out.geojson")
