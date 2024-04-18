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
time_limit = 15

if platformConfig.name == "perlmutter":
    baseline["ngpus"] = 1
    baseline["ntasks_per_node"] = 4
elif platformConfig.name == "ookami":
    baseline["spack_env"] = "hpx-lci-bell24-test"
    time_limit = 60
    baseline["stop_step"] = 10

problems = [
    # {"scenario": "dwd-l10-close_to_merger", "nnodes": [1, 2, 4, 8, 16, 32]},
    # {"scenario": "dwd-l11-close_to_merger", "nnodes": [1, 2, 4]},
    # {"scenario": "dwd-l12-close_to_merger", "nnodes": [32]},
    # {"scenario": "dwd-l10-close_to_merger", "nnodes": [256, 512]},
    # {"scenario": "dwd-l11-close_to_merger", "nnodes": [1500]},
    # {"scenario": "dwd-l12-close_to_merger", "nnodes": [256]},
    {"scenario": "dwd-l12-close_to_merger", "nnodes": [512]},
]

configs = [
    # # # LCI v.s. MPI
    {**baseline, "name": "lci", "parcelport": "lci"},
    {**baseline, "name": "mpi", "parcelport": "mpi", "sendimm": 0},
]
def config_fn(config):
    config["name"] = config["scenario"] + "-" + config["name"]
    return config


if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, update_outside=problems, time=time_limit, config_fn=config_fn)