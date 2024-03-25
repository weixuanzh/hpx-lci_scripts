#!/usr/bin/env python3

import os
import sys
import shutil
import copy
import json
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "mpi",
    "spack_env": "hpx-lcw-sc24",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nthreads": 128,
    "min_size": 8,
    "max_size": 65536,
    "test_mode": 0,
    "niters": 1000,
    "ndevices": 1,
    "lcw_backend": "mpi"
}
matrix_outside = ["nnodes"]
matrix_inside = []
time = 1

if platformConfig.name == "rostam":
    baseline["spack_env"] = "hpx-lcw-openmpi"
    baseline["nthreads"] = 40

configs = [
    # baseline,
    {**baseline, "name": "lci", "lcw_backend": "lci"},
    {**baseline, "name": "mpi"}
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, time=time)