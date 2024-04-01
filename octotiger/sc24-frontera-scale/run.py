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
    "spack_env": "hpx-lcw-sc24-test",
    "nnodes": [32],
    "ntasks_per_node": 1,
    "griddim": 8,
    "max_level": 5,
    "stop_step": 5,
    "zc_threshold": 8192,
    "scenario": "rs",
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "comp_type_header": "queue",
    "comp_type_followup": "queue",
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
matrix_outside = ["nnodes"]
matrix_inside = []
time_limit = 3

configs1 = [
    # # # LCI v.s. MPI
    # {**baseline, "name": "lci", "nnodes": [256, 512], "parcelport": "lci"},
    {**baseline, "name": "lci", "nnodes": [128], "parcelport": "lci", "ntasks_per_node": 4},
    {**baseline, "name": "lci", "nnodes": [32], "parcelport": "lci", "ntasks_per_node": 16},
]

configs = configs1

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, time=time_limit)