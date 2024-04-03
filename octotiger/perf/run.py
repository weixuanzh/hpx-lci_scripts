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
    "name": "mpi",
    "spack_env": "hpx-lcw",
    "nnodes": [32],
    "ntasks_per_node": 1,
    "griddim": 8,
    "max_level": 5,
    "stop_step": 5,
    "zc_threshold": 8192,
    "scenario": "rs",
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "comp_type": "queue",
    "progress_type": "worker",
    "prg_thread_num": "auto",
    "sendimm": 1,
    "backlog_queue": 0,
    "prepost_recv_num": 1,
    "zero_copy_recv": 1,
    # "in_buffer_assembly": 1,
    "match_table_type": "hashqueue",
    "cq_type": "array_atomic_faa",
    "reg_mem": 1,
    "ndevices": 2,
    "ncomps": 1,
    "perf": "record"
}
time_limit=3

if platformConfig.name == "perlmutter":
    baseline["ngpus"] = 1
if platformConfig.name == "expanse":
    baseline["spack_env"] = "hpx-lcw-sc24"
    baseline["ntasks_per_node"] = 2
    baseline["nnodes"] = [32]
if platformConfig.name == "delta":
    baseline["spack_env"] = "hpx-lcw-sc24"
    baseline["ntasks_per_node"] = 2
    baseline["nnodes"] = [32]
if platformConfig.name == "frontera":
    baseline["spack_env"] = "hpx-lcw-sc24"
    baseline["nnodes"] = [32]

configs = [
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    # {**baseline, "name": "mpi_a", "parcelport": "mpi", "sendimm": 0},
    {**baseline, "name": "lci", "parcelport": "lci"},
    {**baseline, "name": "lci_global_b", "parcelport": "lci", "lock_mode": "global_b"},
    # {**baseline, "name": "lci_pin", "progress_type": "pin"},
    # {**baseline, "name": "lci_mutex", "parcelport": "lci", "cq_type": "array_mutex"},
    # {**baseline, "name": "mpi", "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "lcw", "parcelport": "lcw", "sendimm": 0},
    # {**baseline, "name": "lcw_i", "parcelport": "lcw"},
    # {**baseline, "name": "lcw_i_mt_d2_c1", "parcelport": "lcw", "ndevices": 2, "progress_type": "worker", "ncomps": 1},
    # {**baseline, "name": "lcw_i_mt_d28_c1", "parcelport": "lcw", "ndevices": 28, "progress_type": "worker", "ncomps": 1},
    # {**baseline, "name": "lci_mt_d28_c1", "parcelport": "lci", "ndevices": 28, "progress_type": "worker",
    #  "ncomps": 1},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, config_fn=None, time=time_limit)