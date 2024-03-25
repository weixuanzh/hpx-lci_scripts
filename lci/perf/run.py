#!/usr/bin/env python3

import os
import sys
import shutil
import copy
import json
sys.path.append("../../include")
from script_common import *
import time

baseline = {
    "name": "hello_world",
    "spack_env": "hpx-lcw",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "args": ["lci_hello_world"]
}

matrix_outside = ["nnodes"]
matrix_inside = []
time_limit = 1

configs = [
    # baseline,
    # {**baseline, "name": "many2many_random", "args": ["lci_many2many_random", "--size", "40800", "--nthreads", "16"]}
    # {**baseline, "name": "pt2pt",
    #  "args": ["lci_lcitb_pt2pt", "--min-msg-size", "8192", "--nsteps", "1000", "--nthreads", "128"]},
    {**baseline, "name": "lcw_pingpong",
     "args": ["lcw_pingpong_mt", "--min-size", "8192", "--niters", "1000", "--nthreads", "128", "--test-mode=0"]}
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, time=time_limit)