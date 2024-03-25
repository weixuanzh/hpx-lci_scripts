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
    "name": "pingpong-lci",
    "spack_env": "hpx-lcw",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nbytes": [8],
    "nchains": [1000000],
    "nsteps": [1],
    "intensity": [0],
    "batch_size": 100,
    "is_single_source": "1",
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "nthreads": [None],
    "comp_type_header": "queue",
    "comp_type_followup": "queue",
    "progress_type": "worker",
    "prg_thread_num": "auto",
    "sendimm": 1,
    "backlog_queue": 0,
    "prepost_recv_num": 1,
    "zero_copy_recv": 1,
    "agas_caching": 0,
    # "in_buffer_assembly": 1,
    "match_table_type": "hashqueue",
    "cq_type": "array_atomic_faa",
    "reg_mem": 1,
    "ndevices": 2,
    "ncomps": 1,
    "lcw_backend": "mpi"
}
if platformConfig.name == "rostam":
    baseline["spack_env"] = "hpx-lcw-openmpi"
if platformConfig.name == "delta":
    baseline["spack_env"] = "hpx-lcw-sc24"
    # pass
if platformConfig.name == "expanse":
    baseline["spack_env"] = "hpx-lcw"
matrix_outside = ["nnodes"]
matrix_inside = ["nbytes", "nchains", "nsteps", "intensity", "nthreads"]
time_limit = 1

configs = [
    # baseline,
    # {**baseline, "name": "lci", "parcelport": "lci"},
    {**baseline, "name": "lci_header_sync_single_nolock_poll", "ncomps": 2, "protocol": "sendrecv",
     "comp_type_header": "sync_single_nolock", "progress_type": "poll", "bg_work_when_send": 0},
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    # {**baseline, "name": "lcw_mpi", "parcelport": "lcw"},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, config_fn=None, time=time_limit)