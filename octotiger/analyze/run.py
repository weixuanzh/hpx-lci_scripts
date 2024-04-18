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
    "name": "lci",
    "spack_env": "hpx-lci-analyze",
    "nnodes": [32],
    "ntasks_per_node": 1,
    "ngpus": 0,
    "scenario": "dwd-l10-close_to_merger",
    "stop_step": 25,
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "comp_type": "queue",
    "progress_type": "worker",
    "prg_thread_num": "auto",
    "sendimm": 1,
    "backlog_queue": 0,
    "prepost_recv_num": 1,
    "in_buffer_assembly": 1,
    "match_table_type": "hashqueue",
    "cq_type": "array_atomic_faa",
    "reg_mem": 1,
    "ndevices": 2,
    "ncomps": 1,
}
time_limit = 2

if platformConfig.name == "perlmutter":
    baseline["ntasks_per_node"] = 4
    baseline["ngpus"] = 1
    baseline["stop_step"] = 25
    baseline["scenario"] = "dwd-l10-close_to_merger"

if platformConfig.name == "delta":
    baseline["nnodes_list"] = [32]
    baseline["ntasks_per_node"] = 4
    baseline["stop_step"] = 5
    # baseline["scenario"] = "dwd-l10-beginning"
    baseline["scenario"] = "dwd-l10-close_to_merger"

if platformConfig.name == "polaris":
    baseline["spack_env"] = "hpx-lci"
    baseline["nnodes_list"] = [4, 8, 16, 32]
    baseline["ntasks_per_node"] = 4
    baseline["ngpus"] = 1

configs = [
    # # # LCI v.s. MPI
    # {**baseline, "name": "lcw", "parcelport": "lcw", "sendimm": 0},
    {**baseline, "name": "lci", "parcelport": "lci"},
    # {**baseline, "name": "mpi", "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi_i", "parcelport": "mpi", "sendimm": 1},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, time=time_limit)