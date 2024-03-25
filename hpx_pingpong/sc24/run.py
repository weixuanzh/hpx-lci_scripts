#!/usr/bin/env python3
import sys
sys.path.append("../../include")
from script_common import *

baseline = {
    "name": "pingpong-lci",
    "spack_env": "hpx-lcw-sc24",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "nbytes": [16384],
    "nchains": [1024],
    "nsteps": [1000],
    "intensity": [0],
    "task_comp_time": [0],
    "batch_size": 10,
    "is_single_source": 0,
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
# BATCH SIZE?

matrix_outside = ["nnodes"]
matrix_inside = ["nbytes", "nchains", "nsteps", "intensity", "nthreads", "task_comp_time"]
time = 20

flood_16k_nchains = 100000
nthreads = []
if platformConfig.name == "expanse":
    nthreads = [128, 64, 32, 16, 8, 4, 2, 1]
elif platformConfig.name == "frontera":
    nthreads = [56, 28, 14, 7, 4, 2, 1]
elif platformConfig.name == "delta":
    nthreads = [128, 64, 32, 16, 8, 4, 2, 1]
    flood_16k_nchains = 10000

# if platformConfig.name == "delta":
#     baseline["bg_work_when_send"] = 0

hpx_configs1 = [
    {"name": "lci", "parcelport": "lci"},
    {"name": "mpi", "parcelport": "mpi"},
    {"name": "mpi_a", "parcelport": "mpi", "sendimm": "0"},
]

pingpong_configs1 = [
    {"pingpong_config_name": "flood", "nchains": [1000000], "nsteps": [1], "is_single_source": 1, "nbytes": [8], "batch_size": 100, "nthreads": nthreads},
    {"pingpong_config_name": "flood", "nchains": [flood_16k_nchains], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10, "nthreads": nthreads},
    {"pingpong_config_name": "nchains", "nbytes": [8, 16384], "nchains": [1, 4, 16, 64, 256, 1024, 4096]},
    {"pingpong_config_name": "nbytes", "nbytes": [16, 64, 256, 1024, 4096, 16384, 65536]},
    {"pingpong_config_name": "comp", "task_comp_time": [1, 10, 100, 1000]},
]

hpx_configs2 = [
    # # LCI v.s. MPI
    # communication prototype
    {"name": "lci_sendrecv", "protocol": "sendrecv"},
    # completion type: header
    {"name": "lci_header_sync_single", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single"},
    {"name": "lci_header_sync_single_nolock", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock"},
    {"name": "lci_header_sync_single_poll", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single", "progress_type": "poll"},
    {"name": "lci_header_sync_single_nolock_poll", "ncomps": 2, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock", "progress_type": "poll"},
    # completion type: followup
    {"name": "lci_followup_queue_mutex", "cq_type": "array_mutex"},
    {"name": "lci_followup_sync", "comp_type_followup": "sync"},
    {"name": "lci_followup_sync_poll", "comp_type_followup": "sync", "progress_type": "poll"},
    {"name": "lci_followup_2queue", "ncomps": 2},
    # # progress type
    {"name": "lci_pin", "progress_type": "rp"},
    {"name": "lci_pthread", "progress_type": "pthread"},
    {"name": "lci_pthread_worker", "progress_type": "pthread_worker"},
    # device lock
    {"name": "lci_global_d1", "ndevices": 1, "parcelport": "lci", "lock_mode": "global"},
    {"name": "lci_global_d2", "ndevices": 2, "parcelport": "lci", "lock_mode": "global"},
    {"name": "lci_global_d4", "ndevices": 4, "parcelport": "lci", "lock_mode": "global"},
    {"name": "lci_global_d8", "ndevices": 8, "parcelport": "lci", "lock_mode": "global"},
    {"name": "lci_global_d16", "ndevices": 16, "parcelport": "lci", "lock_mode": "global"},
    {"name": "lci_global_b_d1", "ndevices": 1, "parcelport": "lci", "lock_mode": "global_b"},
    {"name": "lci_global_b_d2", "ndevices": 2, "parcelport": "lci", "lock_mode": "global_b"},
    {"name": "lci_global_b_d4", "ndevices": 4, "parcelport": "lci", "lock_mode": "global_b"},
    {"name": "lci_global_b_d8", "ndevices": 8, "parcelport": "lci", "lock_mode": "global_b"},
    {"name": "lci_global_b_d16", "ndevices": 16, "parcelport": "lci", "lock_mode": "global_b"},
    # ndevices + progress_type
    {"name": "lci_mt_d1_c1", "ndevices": 1, "progress_type": "worker", "ncomps": 1},
    {"name": "lci_mt_d2_c1", "ndevices": 2, "progress_type": "worker", "ncomps": 1},
    {"name": "lci_mt_d4_c1", "ndevices": 4, "progress_type": "worker", "ncomps": 1},
    {"name": "lci_mt_d8_c1", "ndevices": 8, "progress_type": "worker", "ncomps": 1},
    {"name": "lci_mt_d16_c1", "ndevices": 16, "progress_type": "worker", "ncomps": 1},
    {"name": "lci_pin_d1_c1", "ndevices": 1, "progress_type": "rp", "ncomps": 1},
    {"name": "lci_pin_d2_c1", "ndevices": 2, "progress_type": "rp", "ncomps": 1},
    {"name": "lci_pin_d4_c1", "ndevices": 4, "progress_type": "rp", "ncomps": 1},
    {"name": "lci_pin_d8_c1", "ndevices": 8, "progress_type": "rp", "ncomps": 1},
    {"name": "lci_pin_d16_c1", "ndevices": 16, "progress_type": "rp", "ncomps": 1},
    # Aggregation
    {"name": "lci_a", "sendimm": 0},
]

pingpong_configs2 = [
    {"pingpong_config_name": "flood", "nchains": [1000000], "nsteps": [1], "is_single_source": 1, "nbytes": [8], "batch_size": 100},
    {"pingpong_config_name": "flood", "nchains": [flood_16k_nchains], "nsteps": [1], "is_single_source": 1, "nbytes": [16384], "batch_size": 10},
    {"pingpong_config_name": "nchains", "nbytes": [8, 16384], "nchains": [1024]},
    {"pingpong_config_name": "comp", "nbytes": [16384], "task_comp_time": [1000]},
]

hpx_configs3 = [
    # # LCI baseline
    {"name": "lci_baseline", "progress_type": "rp", "ndevices": 1},
    # communication prototype
    {"name": "lci_sendrecv", "progress_type": "rp", "ndevices": 1, "protocol": "sendrecv"},
    # completion type: header
    {"name": "lci_header_sync_single", "progress_type": "rp", "ndevices": 1, "protocol": "sendrecv", "comp_type_header": "sync_single"},
    {"name": "lci_header_sync_single_nolock", "progress_type": "rp", "ndevices": 1, "protocol": "sendrecv", "comp_type_header": "sync_single_nolock"},
    # completion type: followup
    {"name": "lci_followup_queue_mutex", "progress_type": "rp", "ndevices": 1, "cq_type": "array_mutex"},
    {"name": "lci_followup_sync", "progress_type": "rp", "ndevices": 1, "comp_type_followup": "sync"},
    # # progress type
    {"name": "lci_mt", "ndevices": 1, "progress_type": "worker"},
    {"name": "lci_pthread", "ndevices": 1, "progress_type": "pthread"},
    {"name": "lci_pthread_worker", "ndevices": 1, "progress_type": "pthread_worker"},
]

# update_outside = None
# update_inside = None
# configs = dict_product(baseline, hpx_configs1, pingpong_configs1)
# configs = [baseline]
# update_outside = hpx_configs2
# update_inside = pingpong_configs2
configs = [baseline]
update_outside = hpx_configs3
update_inside = pingpong_configs2

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_outside, matrix_inside, update_outside, update_inside, time=time)