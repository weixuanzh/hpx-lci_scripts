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
    "spack_env": "hpx-lci",
    "nnodes_list": [1],
    "ntasks_per_node": 4,
    "griddim": 8,
    "max_level": 4,
    "stop_step": 5,
    "zc_threshold": 4096,
    "task": "rs",
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
    "ndevices": 1,
    "ncomps": 1,
    "lcipp_log_level": "debug"
}

if platformConfig.name == "perlmutter":
    baseline["ngpus"] = 1

configs = [
    {**baseline, "name": "lci", "parcelport": "lci"},
]
run_as_one_job = False

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    tag = getenv_or("RUN_TAG", "default")
    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))
    if run_as_one_job:
        for config in configs:
            if len(config["nnodes_list"]) > 1:
                print("Cannot run as one job! Give up!")
                exit(1)

    root_path = os.path.realpath(os.path.join(get_current_script_path(), "../.."))
    for i in range(n):
        if run_as_one_job:
            for nnodes in configs[0]["nnodes_list"]:
                spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, configs[0]["spack_env"]))
                run_slurm(tag, nnodes, configs, name="all", time = "00:00:{}".format(len(configs) * 30))
        else:
            for config in configs:
                spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, config["spack_env"]))
                # print(config)
                for nnodes in config["nnodes_list"]:
                    run_slurm(tag, nnodes, config, time = "10:00")