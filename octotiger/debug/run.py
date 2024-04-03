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
    "spack_env": "hpx-lcw",
    "nnodes": [2],
    "ntasks_per_node": 4,
    "griddim": 8,
    "max_level": 5,
    "stop_step": 5,
    "zc_threshold": 8192,
    "scenario": "rs",
    "parcelport": "lci",
    "protocol": "putsendrecv",
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
    "lcw_backend": "mpi",
}
matrix_outside = ["nnodes"]
matrix_inside = []
time_limit = 2

if platformConfig.name == "perlmutter":
    baseline["spack_env"] = "hpx-lci-bell24"
    baseline["ntasks_per_node"] = 4
    baseline["ngpus"] = 1
    baseline["stop_step"] = 5
    # baseline["scenario"] = "dwd-l10-beginning"
    baseline["scenario"] = "dwd-l10-close_to_merger"

if platformConfig.name == "delta":
    baseline["spack_env"] = "hpx-lcw-sc24-griddim2"
    baseline["nnodes"] = [32]
    baseline["ntasks_per_node"] = 1
    baseline["stop_step"] = 5
    baseline["griddim"] = 2
    # baseline["scenario"] = "dwd-l10-beginning"
    # baseline["scenario"] = "dwd-l10-close_to_merger"

if platformConfig.name == "polaris":
    baseline["spack_env"] = "hpx-lcw"
    baseline["nnodes"] = [4, 8, 16, 32]
    baseline["ntasks_per_node"] = 4
    baseline["ngpus"] = 1

if platformConfig.name == "rostam":
    baseline["spack_env"] = "hpx-lcw-openmpi"
    baseline["nnodes"] = [12]
    baseline["ntasks_per_node"] = 1
    baseline["max_level"] = 5
    baseline["griddim"] = 8

if platformConfig.name == "expanse":
    baseline["spack_env"] = "hpx-lcw-sc24"
    baseline["nnodes"] = [2, 4, 8, 16, 32]
    baseline["ntasks_per_node"] = 2
    baseline["griddim"] = 8
    # baseline["scenario"] = "dwd-l10-close_to_merger"
    # baseline["scenario"] = "dwd-l11-close_to_merger"

if platformConfig.name == "frontera":
    baseline["spack_env"] = "hpx-lcw-sc24"
    baseline["nnodes"] = [32]
    baseline["ntasks_per_node"] = 1
    baseline["griddim"] = 8
    # baseline["scenario"] = "dwd-l10-close_to_merger"


configs = [
    # # # LCI v.s. MPI
    # {**baseline, "name": "mpi_a", "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    # {**baseline, "name": "lci_d1", "parcelport": "lci", "ndevices": 1},
    # {**baseline, "name": "lci_mutex", "parcelport": "lci", "cq_type": "array_mutex"},
    {**baseline, "name": "lci", "parcelport": "lci"},
    # {**baseline, "name": "lci_mpi", "parcelport": "lci",
    #  "lock_mode": "global",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync", "ntasks_per_node": 1},
    # {**baseline, "name": "lci_mpi_b", "parcelport": "lci",
    #  "lock_mode": "global_b",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync", "bg_work_max_count": 1},
    # {**baseline, "name": "lci_mpi_b_poll", "parcelport": "lci",
    #  "lock_mode": "global_b",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync", "progress_type": "poll", "bg_work_max_count": 1},
    # {**baseline, "name": "lci_mpi_b_poll_reg", "parcelport": "lci",
    #  "lock_mode": "global_b",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync", "progress_type": "poll", "bg_work_max_count": 1, "enable_sendmc": 1},
    # {**baseline, "name": "lci_mpi_poll", "parcelport": "lci",
    #  "lock_mode": "global",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync", "progress_type": "poll"},
    # {**baseline, "name": "lci_global_d1", "parcelport": "lci", "lock_mode": "global", "ndevices": 1},
    # {**baseline, "name": "lci_global", "parcelport": "lci", "lock_mode": "global"},
    # {**baseline, "name": "lci_global_b_d1", "parcelport": "lci", "lock_mode": "global_b", "ndevices": 1},
    # {**baseline, "name": "lci_header_sync_single_poll", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single", "progress_type": "poll"},
    # {**baseline, "name": "lci_header_sync_single_nolock_poll", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock", "progress_type": "poll"},
    # {**baseline, "name": "lci_sendrecv", "parcelport": "lci", "protocol": "sendrecv"},
    # {**baseline, "name": "lci_sendcrecv", "parcelport": "lci", "protocol": "sendrecv", "enable_sendmc": 1},
    # # completion type: header
    # {**baseline, "name": "lci_header_sync_single", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single"},
    # {**baseline, "name": "lci_header_sync_single_nolock", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock"},
    # # completion type: followup
    # {**baseline, "name": "lci_followup_queue_mutex", "enable_sendmc": 1, "cq_type": "array_mutex"},
    # {**baseline, "name": "lci_followup_sync", "protocol": "sendrecv", "enable_sendmc": 1, "comp_type_followup": "sync"},
    # {**baseline, "name": "lci_followup_2queue", "ncomps": 2},
    # # ndevices + progress_type
    {**baseline, "name": "lci_mt_d1_c1", "ndevices": 1, "progress_type": "worker", "ncomps": 1},
    # {**baseline, "name": "lci_mt_d2_c1", "ndevices": 2, "progress_type": "worker", "ncomps": 1},
    # {**baseline, "name": "lci_mt_d4_c1", "ndevices": 4, "progress_type": "worker", "ncomps": 1},
    {**baseline, "name": "lci_pin_d1_c1", "ndevices": 1, "progress_type": "rp", "ncomps": 1},
    # {**baseline, "name": "lci_pin_d2_c1", "ndevices": 2, "progress_type": "rp", "ncomps": 1},
    # {**baseline, "name": "lci_pin_d4_c1", "ndevices": 4, "progress_type": "rp", "ncomps": 1},
    # {**baseline, "name": "lci-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,},
    # {**baseline, "name": "lci_mpi-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,
    #  "lock_mode": "global",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync"},
    # {**baseline, "name": "lci-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,
    #  "ntasks_per_node": 2},
    # {**baseline, "name": "lci_mpi-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,
    #  "lock_mode": "global",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync",
    #  "ntasks_per_node": 2},
    # {**baseline, "name": "lci-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,
    #  "ntasks_per_node": 4},
    # {**baseline, "name": "lci_mpi-griddim2", "parcelport": "lci",
    #  "spack_env": "hpx-lcw-sc24-griddim2", "griddim": 2,
    #  "lock_mode": "global",
    #  "protocol": "sendrecv", "ndevices": 1,
    #  "comp_type_header": "sync_single", "comp_type_followup": "sync",
    #  "ntasks_per_node": 4},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, time=time_limit)