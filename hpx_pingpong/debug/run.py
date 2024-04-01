#!/usr/bin/env python3
import sys
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "pingpong-lci",
    "spack_env": "hpx-lcw",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nbytes": [16384],
    "nchains": [1024],
    "nsteps": [1000],
    "intensity": [0],
    "task_comp_time": [1000],
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
    # baseline["spack_env"] = "hpx-lcw-mpich-master-debug"
    baseline["spack_env"] = "hpx-lcw-openmpi"
if platformConfig.name == "expanse":
    baseline["spack_env"] = "hpx-lcw-sc24"
if platformConfig.name == "frontera":
    baseline["spack_env"] = "hpx-lcw-sc24"
if platformConfig.name == "delta":
    baseline["spack_env"] = "hpx-lcw-sc24"

# if platformConfig.name == "delta":
#     baseline["bg_work_when_send"] = 0

matrix_outside = ["nnodes"]
matrix_inside = ["nbytes", "nchains", "nsteps", "intensity", "nthreads", "task_comp_time"]
time_limit = 1

configs = [
    # baseline,
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    {**baseline, "name": "lci", "parcelport": "lci"},
    {**baseline, "name": "lci_sendrecv", "protocol": "sendrecv"},
    {**baseline, "name": "lci_sendcrecv", "protocol": "sendrecv", "enable_sendmc": 1},
    {**baseline, "name": "lci_followup_sync", "comp_type_followup": "sync", "enable_sendmc": 1},
    {**baseline, "name": "lci_followup_sync_poll", "comp_type_followup": "sync", "progress_type": "poll", "enable_sendmc": 1},
    # {**baseline, "name": "lci_header_sync_single_nolock_poll", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock", "progress_type": "poll"},
    # {**baseline, "name": "lci_bidir", "parcelport": "lci", "is_single_source": "0"},
    # {**baseline, "name": "lci", "parcelport": "lci", "protocol": "sendrecv"},
    # {**baseline, "name": "lci_sync", "parcelport": "lci", "protocol": "sendrecv", "comp_type_header": "sync"},
    # {**baseline, "name": "lci_sync_single_nolock", "parcelport": "lci", "protocol": "sendrecv", "comp_type_header": "sync_single_nolock"},
    # {**baseline, "name": "lci_sync_single", "parcelport": "lci", "protocol": "sendrecv", "comp_type_header": "sync_single"},
    # {**baseline, "name": "lci_followup_sync", "comp_type_header": "sync", "comp_type_followup": "sync"},
    # {**baseline, "name": "lci_d2", "parcelport": "lci", "ndevices": 2},
    # {**baseline, "name": "lci_d4", "parcelport": "lci", "ndevices": 4},
    # {**baseline, "name": "lci_d10", "parcelport": "lci", "ndevices": 10},
    # {**baseline, "name": "lci_d20", "parcelport": "lci", "ndevices": 20},
    # {**baseline, "name": "lci_d10_c2", "parcelport": "lci", "ndevices": 10, "ncomps": 2},
    # {**baseline, "name": "lci_d10_c4", "parcelport": "lci", "ndevices": 10, "ncomps": 4},
    # {**baseline, "name": "mpi", "parcelport": "mpi"},
    # {**baseline, "name": "lcw_mpi", "parcelport": "lcw"},
    # {**baseline, "name": "lcw_mpi_d1", "parcelport": "lcw", "ndevices": 1},
    # {**baseline, "name": "lcw_mpi_d2", "parcelport": "lcw", "ndevices": 2},
    # {**baseline, "name": "lcw_mpi_d4", "parcelport": "lcw", "ndevices": 4},
    # {**baseline, "name": "lcw_mpi_d8", "parcelport": "lcw", "ndevices": 8},
    # {**baseline, "name": "lcw_mpi_d9", "parcelport": "lcw", "ndevices": 9},
    # {**baseline, "name": "lcw_mpi_d10", "parcelport": "lcw", "ndevices": 10},
    # {**baseline, "name": "lcw_mpi_d20", "parcelport": "lcw", "ndevices": 20},
    # {**baseline, "name": "lcw_mpi_d20_c2", "parcelport": "lcw", "ndevices": 20, "ncomps": 2},
    # {**baseline, "name": "lcw_mpi_d20_c4", "parcelport": "lcw", "ndevices": 20, "ncomps": 4},
    # {**baseline, "name": "lcw_mpi_d40", "parcelport": "lcw", "ndevices": 40},
]

pingpong_configs2 = [
    # {"name": "flood", "nchains": [1000000], "nsteps": [1], "is_single_source": 1, "nbytes": [8], "batch_size": 100},
    {"pingpong_name": "flood", "nchains": [100000], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    {"pingpong_name": "flood", "nchains": [100000], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    {"pingpong_name": "flood", "nchains": [100000], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    # {"name": "flood", "nchains": [100000], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    # {"name": "flood", "nchains": [100000], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    # {"name": "nchains", "nbytes": [8, 16384], "nchains": [1024]},
    # {"name": "comp", "nbytes": [16384], "task_comp_time": [1000]},
]
update_inside = pingpong_configs2
# flat_configs = flatten_configs(configs, matrix_outside, matrix_inside, update_inside=update_inside)
# print(flat_configs)
# exit(0)

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, update_inside=update_inside, time=time_limit)