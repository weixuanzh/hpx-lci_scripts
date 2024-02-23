#!/usr/bin/env python3
import sys
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "pingpong-lci",
    "spack_env": "hpx-lcw",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nbytes": [8],
    "nchains": [50000],
    "nsteps": [1],
    "intensity": [0],
    "is_single_source": "1",
    "parcelport": "lci",
    "protocol": "putsendrecv",
    "nthreads": [None],
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
if platformConfig.name == "rostam":
    # baseline["spack_env"] = "hpx-lcw-mpich-master-debug"
    baseline["spack_env"] = "hpx-lcw-mpich-master"

matrix_outside = ["nnodes"]
matrix_inside = ["nbytes", "nchains", "nsteps", "intensity", "nthreads"]
time_limit = 10

configs = [
    # baseline,
    # {**baseline, "name": "lci", "parcelport": "lci"},
    # {**baseline, "name": "lci_d2", "parcelport": "lci", "ndevices": 2},
    # {**baseline, "name": "lci_d4", "parcelport": "lci", "ndevices": 4},
    # {**baseline, "name": "lci_d10", "parcelport": "lci", "ndevices": 10},
    # {**baseline, "name": "lci_d20", "parcelport": "lci", "ndevices": 20},
    # {**baseline, "name": "lci_d10_c2", "parcelport": "lci", "ndevices": 10, "ncomps": 2},
    # {**baseline, "name": "lci_d10_c4", "parcelport": "lci", "ndevices": 10, "ncomps": 4},
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    # {**baseline, "name": "lcw_mpi", "parcelport": "lcw"},
    {**baseline, "name": "lcw_mpi_d1", "parcelport": "lcw", "ndevices": 1},
    {**baseline, "name": "lcw_mpi_d2", "parcelport": "lcw", "ndevices": 2},
    {**baseline, "name": "lcw_mpi_d4", "parcelport": "lcw", "ndevices": 4},
    {**baseline, "name": "lcw_mpi_d8", "parcelport": "lcw", "ndevices": 8},
    {**baseline, "name": "lcw_mpi_d9", "parcelport": "lcw", "ndevices": 9},
    {**baseline, "name": "lcw_mpi_d10", "parcelport": "lcw", "ndevices": 10},
    {**baseline, "name": "lcw_mpi_d20", "parcelport": "lcw", "ndevices": 20},
    {**baseline, "name": "lcw_mpi_d20_c2", "parcelport": "lcw", "ndevices": 20, "ncomps": 2},
    {**baseline, "name": "lcw_mpi_d20_c4", "parcelport": "lcw", "ndevices": 20, "ncomps": 4},
    {**baseline, "name": "lcw_mpi_d40", "parcelport": "lcw", "ndevices": 40},
]
def config_fn(config):
    if "-nthreads" in config["name"]:
        config["nchains"] = config["nthreads"] * 8
    return config

# flat_configs = flatten_configs(configs, matrix_outside, matrix_inside, config_fn)
# print(flat_configs)
# exit(0)

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, config_fn=config_fn, time=time_limit)