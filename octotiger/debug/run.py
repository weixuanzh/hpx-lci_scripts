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
    "max_level": 3,
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
    baseline["ngpus"] = 0

configs = [
    # # # LCI v.s. MPI
    {**baseline, "name": "lci", "parcelport": "lci"},
    # {**baseline, "name": "mpi", "parcelport": "mpi", "sendimm": 0},
    # # {**baseline, "nnodes_list": [2, 4, 8, 16, 32], "name": "mpi_i", "parcelport": "mpi", "sendimm": 1},
    # # # Different Problem Size
    # # {**baseline, "name": "mpi-grid4", "parcelport": "mpi", "sendimm": 0, "griddim": 4},
    # # {**baseline, "name": "mpi-grid6", "parcelport": "mpi", "sendimm": 0, "griddim": 6},
    # # {**baseline, "name": "mpi-grid8", "parcelport": "mpi", "sendimm": 0, "griddim": 8},
    # # {**baseline, "name": "mpi_i-grid4", "parcelport": "mpi", "sendimm": 1, "griddim": 4},
    # # {**baseline, "name": "mpi_i-grid6", "parcelport": "mpi", "sendimm": 1, "griddim": 6},
    # # # {**baseline, "name": "mpi_i-grid8", "parcelport": "mpi", "sendimm": 1, "griddim": 8},
    # {**baseline, "name": "lci-grid4", "parcelport": "lci", "griddim": 4},
    # {**baseline, "name": "lci-grid6", "parcelport": "lci", "griddim": 6},
    # {**baseline, "name": "lci-grid8", "parcelport": "lci", "griddim": 8},
    # # communication prototype + comp_type
    # {**baseline, "name": "lci_sendrecv", "protocol": "sendrecv"},
    # {**baseline, "name": "lci_sync", "comp_type": "sync"},
    # # # ndevices + progress_type
    # # {**baseline, "name": "lci_mt_d1_c1", "ndevices": 1, "progress_type": "worker", "ncomps": 1},
    # # {**baseline, "name": "lci_mt_d2_c1", "ndevices": 2, "progress_type": "worker", "ncomps": 1},
    # # {**baseline, "name": "lci_mt_d4_c1", "ndevices": 4, "progress_type": "worker", "ncomps": 1},
    # {**baseline, "name": "lci_mt_d8_c1", "ndevices": 8, "progress_type": "worker", "ncomps": 1},
    # # {**baseline, "name": "lci_pin_d1_c1", "ndevices": 1, "progress_type": "rp", "ncomps": 1},
    # # {**baseline, "name": "lci_pin_d2_c1", "ndevices": 2, "progress_type": "rp", "ncomps": 1},
    # # {**baseline, "name": "lci_pin_d4_c1", "ndevices": 4, "progress_type": "rp", "ncomps": 1},
    # {**baseline, "name": "lci_pin_d8_c1", "ndevices": 8, "progress_type": "rp", "ncomps": 1},
    # # # ncomps
    # # {**baseline, "name": "lci_mt_d4_c2", "ndevices": 4, "progress_type": "worker", "ncomps": 2},
    # # {**baseline, "name": "lci_mt_d4_c4", "ndevices": 4, "progress_type": "worker", "ncomps": 4},
    # # {**baseline, "name": "lci_pin_d4_c2", "ndevices": 4, "progress_type": "rp", "ncomps": 2},
    # # {**baseline, "name": "lci_pin_d4_c4", "ndevices": 4, "progress_type": "rp", "ncomps": 4},
    # # # Upper-layer
    # {**baseline, "name": "lci_wo_i", "sendimm": 0},
    # {**baseline, "name": "lci_alock_wo_i", "special_branch": "ipdps_nohack1", "sendimm": 0},
    # {**baseline, "name": "lci_alock", "special_branch": "ipdps_nohack1"},
    # {**baseline, "name": "lci_tlock", "special_branch": "ipdps_nohack2"},
    # {**baseline, "name": "lci_atlock", "special_branch": "ipdps_nohack12"},
    # {**baseline, "name": "lci_agas_caching", "agas_caching": 1},
    # # # Memory Registration
    # # {**baseline, "name": "lci_worker_cache", "ndevices": 1, "progress_type": "rp", "reg_mem": 1, "mem_reg_cache": 1},
    # # {**baseline, "name": "lci_prg_cache", "ndevices": 1, "progress_type": "rp", "reg_mem": 0, "mem_reg_cache": 1},
    # # {**baseline, "name": "lci_worker_nocache", "ndevices": 1, "progress_type": "rp", "reg_mem": 1, "mem_reg_cache": 0},
    # # {**baseline, "name": "lci_prg_nocache", "ndevices": 1, "progress_type": "rp", "reg_mem": 0, "mem_reg_cache": 0},
    # # Memory Copy
    # {**baseline, "name": "lci_wo_in_buffer", "parcelport": "lci", "in_buffer_assembly": 0},
    # {**baseline, "name": "lci_wo_zc_recv", "parcelport": "lci", "zero_copy_recv": 0},
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
                    run_slurm(tag, nnodes, config, time = "5:00")