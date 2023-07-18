#!/usr/bin/env python3
#encoding: utf-8

from crbranch.branch import Branch
from crbranch.crbranch import CrBranch

crbranch = CrBranch()
crbranch.load_data(osm_file = "data/example_clermont_18_07_2023.osm")
branch = Branch.load_example_001()

crbranch.build_branch(branch)

crbranch.json_export("/tmp/out.json")
