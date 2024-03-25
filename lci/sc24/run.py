#!/usr/bin/env python3

import os
import sys
import shutil
import copy
import json
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "hello_world",
    "spack_env": "hpx-lcw-sc24",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "args": ["lci_hello_world"]
}

nthreads = get_platform_config("cpus_per_node", {}, 0)
configs = [
    # baseline,
    {**baseline, "name": "mpi", "args": ["lci_mpi_pt2pt",
                                         "--max-msg-size=65536",
                                         "--nthreads={}".format(nthreads),
                                         "--thread-pin=1"]},
    {**baseline, "name": "lci", "args": ["lci_lcitb_pt2pt",
                                         "--op=2m",
                                         "--max-msg-size=8192",
                                         "--nthreads={}".format(nthreads),
                                         "--thread-pin=1"]},
    {**baseline, "name": "lci", "args": ["lci_lcitb_pt2pt",
                                         "--op=2l",
                                         "--min-msg-size=16384",
                                         "--max-msg-size=65536",
                                         "--nthreads={}".format(nthreads),
                                         "--thread-pin=1"]}
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs)