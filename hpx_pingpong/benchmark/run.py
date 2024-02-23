#!/usr/bin/env python3
import sys
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "pingpong-lci",
    "spack_env": "hpx-lcw-amd",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nbytes": [16384],
    "nchains": [1024],
    "nsteps": [1000],
    "intensity": [0],
    "enable_comp_timer": 0,
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
    "ndevices": [1],
    "ncomps": 1,
    "lcw_backend": "mpi"
}
if platformConfig.name == "rostam":
    # baseline["spack_env"] = "hpx-lcw-mpich-master-debug"
    baseline["spack_env"] = "hpx-lcw-mpich-master"
matrix_outside = ["nnodes", "ndevices"]
matrix_inside = ["nbytes", "nchains", "nsteps", "intensity", "nthreads"]
time = 10

configs = [
    # baseline,
    {**baseline, "name": "lci-nbytes", "nbytes": [16, 64, 256, 1024, 4096, 16384, 65536], "parcelport": "lci", "ndevices": [1, 2, 4, 8, 10, 20]},
    {**baseline, "name": "lci-nchains", "nbytes": [8, 16384], "nchains": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 2048, 4096], "parcelport": "lci", "ndevices": [1, 2, 4, 8, 10, 20]},
    # {**baseline, "name": "lci-intensity", "intensity": [1, 30, 350, 3370, 40000], "enable_comp_timer": 1},
    # {**baseline, "name": "lci-nthreads", "nbytes": [8, 16384], "nthreads": [1, 2, 4, 8, 16, 32, 64]},
    #
    {**baseline, "name": "mpi-nbytes", "nbytes": [16, 64, 256, 1024, 4096, 16384, 65536], "parcelport": "mpi"},
    {**baseline, "name": "mpi-nchains", "nbytes": [8, 16384], "nchains": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 2048, 4096], "parcelport": "mpi"},
    # {**baseline, "name": "mpi-nbytes", "nbytes": [8, 16384, 256*1024], "parcelport": "mpi"},
    # {**baseline, "name": "mpi-nchains", "nchains": [256, 512, 2048, 4096], "parcelport": "mpi"},
    # {**baseline, "name": "mpi-intensity", "intensity": [55, 620, 6250], "parcelport": "mpi", "enable_comp_timer": 1},
    # {**baseline, "name": "mpi-nbytes", "nbytes": [16, 64, 256, 1024, 4096, 65536], "parcelport": "mpi"},
    # {**baseline, "name": "mpi-nchains", "nchains": [1, 2, 4, 8, 16, 32, 64, 128], "parcelport": "mpi"},
    # {**baseline, "name": "mpi-intensity", "intensity": [1, 30, 350, 3370, 40000], "parcelport": "mpi", "enable_comp_timer": 1},
    # {**baseline, "name": "mpi-nthreads", "nbytes": [8, 16384], "nthreads": [1, 2, 4, 8, 16, 32, 64], "parcelport": "mpi"},
    #
    # {**baseline, "name": "mpi_a-nbytes", "nbytes": [8, 16384, 256*1024], "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi_a-nchains", "nbytes": [8, 16384], "nchains": [256, 512, 2048, 4096], "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi_a-intensity", "intensity": [55, 620, 6250], "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi_a-nchains", "nbytes": [8, 16384], "nchains": [1, 2, 4, 8, 16, 32, 64, 128], "parcelport": "mpi", "sendimm": 0},
    # {**baseline, "name": "mpi_a-nthreads", "nbytes": [8, 16384], "nthreads": [1, 2, 4, 8, 16, 32, 64], "parcelport": "mpi", "sendimm": 0},

    {**baseline, "name": "lcw-nbytes", "nbytes": [16, 64, 256, 1024, 4096, 16384, 65536], "parcelport": "lcw", "ndevices": [1, 2, 4, 8, 10, 20]},
    {**baseline, "name": "lcw-nchains", "nbytes": [8, 16384], "nchains": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 2048, 4096], "parcelport": "lcw", "ndevices": [1, 2, 4, 8, 10, 20]},
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
        submit_jobs(configs, matrix_outside, matrix_inside, config_fn=config_fn, time=time)