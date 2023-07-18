#!/usr/bin/env python3
#encoding: utf-8

from crbranch.branch import Branch
from crbranch.crbranch import CrBranch
from crbranch.footpath import Footpath

crbranch = CrBranch()
crbranch.load_data(lat=45.77349, lng=3.09111)

crbranch.build_branches()

crbranch.json_export("/tmp/out.json")
