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
    "spack_env": "hpx-lcw-sc24",
    "nnodes": [1],
    "ntasks_per_node": 1,
    "args": ["lci_hello_world"]
}

time_limit = 1

configs = [
    # baseline,
    # {**baseline, "name": "hello_world_scale", "args": ["--mpi=pmi2", "lci_hello_world"], "nnodes": [512]},
    # {**baseline, "name": "hello_world_scale", "args": ["--mpi=pmix", "lci_hello_world"], "nnodes": [512]},
    # {**baseline, "name": "hello_world_scale", "args": ["--mpi=pmi2", "lci_hello_world"], "nnodes": [16], "ntasks_per_node": 32},
    # {**baseline, "name": "hello_world_scale", "args": ["--mpi=pmix", "lci_hello_world"], "nnodes": [16], "ntasks_per_node": 32},
    {**baseline, "name": "hello_world_scale", "args": ["--mpi=pmix", "lci_hello_world"], "nnodes": [1], "ntasks_per_node": 32},
    # {**baseline, "name": "many2many_random", "args": ["lci_many2many_random", "--size", "40800", "--nthreads", "16"]}
    # {**baseline, "name": "pt2pt", "args": ["lci_lcitb_pt2pt", "--max-msg-size", "8"]}
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, time=time_limit)