#!/usr/bin/env python3

import os
import sys
import shutil
import copy
import json
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "lci",
    "spack_env": "hpx-lci-bell24",
    "nnodes": [1, 2, 4, 8, 16, 32],
    "ntasks_per_node": 4,
    "ngpus": 1,
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
    "zero_copy_recv": 1,
    "in_buffer_assembly": 1,
    "match_table_type": "hashqueue",
    "cq_type": "array_atomic_faa",
    "reg_mem": 1,
    "ndevices": 2,
    "ncomps": 1,
}
time_limit = 1

problems = [
    # {"scenario": "dwd-l10-close_to_merger", "nnodes": [256, 512]},
    # {"scenario": "dwd-l10-beginning", "nnodes": [1, 2, 4, 8, 16, 32]},
    # {"scenario": "dwd-l11-close_to_merger", "nnodes": [512, 1024, 1250]},
    # {"scenario": "dwd-l11-beginning", "nnodes": [32]},
    {"scenario": "dwd-l12-close_to_merger", "nnodes": [1250, 1500]},
    # {"scenario": "dwd-l12-beginning", "nnodes": [64, 128, 256, 512]},
    # {"scenario": "dwd-l10-close_to_merger", "nnodes": [32]},
    # {"scenario": "dwd-l11-close_to_merger", "nnodes": [1024, 1250]},
    # {"scenario": "dwd-l12-close_to_merger", "nnodes": [512]},
]

configs = [
    # # # LCI v.s. MPI
    {**baseline, "name": "lci", "parcelport": "lci"},
    {**baseline, "name": "mpi", "parcelport": "mpi", "sendimm": 0},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, update_outside=problems, time=time_limit)