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
    "name": "hello_world",
    "spack_env": "hpx-lcw",
    "nnodes_list": [2],
    "ntasks_per_node": 1,
    "args": ["lci_hello_world"]
}

configs = [
    # baseline,
    # {**baseline, "name": "many2many_random", "args": ["lci_many2many_random", "--size", "40800", "--nthreads", "16"]}
    {**baseline, "name": "pt2pt", "args": ["lci_lcitb_pt2pt", "--max-msg-size", "8"]}
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
                    time ="1:00"
                    if get_platform_config('name', config) == "polaris":
                        time = "5:00"
                    submit_job("slurm.py", tag, nnodes, config, time=time)