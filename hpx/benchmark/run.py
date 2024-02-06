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
    "name": "pingpong",
    "spack_env": "hpx-lcw",
    "nnodes_list": [2],
    "ntasks_per_node": 1,
    "args": ["pingpong_performance2", "--nbytes=8", "--nchains=1024", "--nsteps=10000"],
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "comp_type": "queue",
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

configs = []
for parcelport in ["lci"]:
    # for nbytes in [8, 16384, 256*1024]:
    for nbytes in [16384]:
        # for intensity in [0]:
        for intensity in [0, 50, 500]:
            for nchains in [256, 512, 1024, 2048, 4096]:
                configs.append({**baseline, "args": ["pingpong_performance2",
                                                     "--nbytes={}".format(nbytes),
                                                     "--nchains={}".format(nchains),
                                                     "--intensity={}".format(intensity),
                                                     "--nsteps=1000",
                                                     "--enable-comp-timer=1"]})

run_as_one_job = True

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
    if run_as_one_job:
        spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, configs[0]["spack_env"]))
        for nnodes in configs[0]["nnodes_list"]:
            for i in range(n):
                submit_job("slurm.py", tag, nnodes, configs, name="all", time ="00:00:{}".format(len(configs) * 30))
    else:
        current_spack_env = None
        for config in configs:
            if current_spack_env != config["spack_env"]:
                spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, config["spack_env"]))
                current_spack_env = config["spack_env"]
            # print(config)
            for nnodes in config["nnodes_list"]:
                config["nnodes"] = nnodes
                for i in range(n):
                    time ="10:00"
                    if get_platform_config('name', config) == "polaris":
                        time = "5:00"
                    submit_job("slurm.py", tag, nnodes, config, time=time)