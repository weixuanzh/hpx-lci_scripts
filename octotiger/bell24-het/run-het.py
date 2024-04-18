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
    "ntasks_per_node": 1,
    "ngpus": 0,
    "scenario": "dwd-l11-close_to_merger",
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
    "het_groups": [
        {"name": "40g", "nnodes": 16, "extra_args": ["--constraint=\"gpu&hbm40g\"", "--gpus-per-node=1"]},
        {"name": "80g", "nnodes": 16, "extra_args": ["--constraint=\"gpu&hbm80g\"", "--gpus-per-node=1"]},
    ]
}
time_limit = 2

if platformConfig.name == "perlmutter":
    baseline["ngpus"] = 1
    baseline["ntasks_per_node"] = 4
elif platformConfig.name == "ookami":
    time_limit = 10
    baseline["stop_step"] = 10

# problems = [
#     # {"scenario": "dwd-l10-close_to_merger", "nnodes": [1, 2, 4, 8, 16, 32]},
#     # {"scenario": "dwd-l11-close_to_merger", "nnodes": [8, 16, 32]},
#     # {"scenario": "dwd-l12-close_to_merger", "nnodes": [32]},
#     {"scenario": "dwd-l10-close_to_merger", "nnodes": [64, 128, 256, 512]},
#     {"scenario": "dwd-l11-close_to_merger", "nnodes": [64, 128, 256, 512, 1024, 1250]},
#     {"scenario": "dwd-l12-close_to_merger", "nnodes": [64, 128, 256, 512, 1024, 1250]},
# ]

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
        root_path = os.path.realpath(os.path.join(get_current_script_path(), "../.."))
        flat_configs = flatten_configs(configs, [], [], None, None, config_fn)
        current_spack_env = None
        for configs in flat_configs:
            common_config = intersect_dicts(configs)
            if current_spack_env != common_config["spack_env"]:
                spack_env_activate(
                    os.path.join(root_path, "spack_env", platformConfig.name, common_config["spack_env"]))
                current_spack_env = common_config["spack_env"]
            pshell.run("export CURRENT_PATH={}".format(get_current_script_path()))
            pshell.run("export CONFIGS=\'{}\'".format(json.dumps(configs)))
            name = common_config["name"]
            nnodes = 0
            nnodes_str = ""
            for het_group in common_config["het_groups"]:
                nnodes += het_group["nnodes"]
                nnodes_str += "-" + het_group["name"] + "_" + str(het_group["nnodes"])
            nnodes_str = str(nnodes) + nnodes_str
            common_config["nnodes"] = nnodes
            job_name = "n{}-{}".format(nnodes_str, name)
            output_filename = "./run/slurm_output.{}.%x.j%j.out".format("het")
            sbatch_args = ["--export=ALL",
                           f"--job-name={job_name}",
                           f"--output={output_filename}",
                           f"--error={output_filename}",
                           f"--time={time_limit}",
                           ]
            if get_platform_config("account", common_config):
                sbatch_args.append("--account={}".format(get_platform_config("account", common_config)))
            partition = get_platform_config("partition", common_config)
            sbatch_args.append("--partition={} ".format(partition))
            qos = get_platform_config("qos", common_config)
            if qos:
                sbatch_args.append("--qos={} ".format(qos))
            for i, het_group in enumerate(common_config["het_groups"]):
                if i != 0:
                    sbatch_args.append(":")
                sbatch_args.append("--nodes={}".format(het_group["nnodes"]))
                sbatch_args.append("--ntasks={}".format(het_group["nnodes"] * common_config["ntasks_per_node"]))
                sbatch_args += het_group["extra_args"]

            current_path = get_current_script_path()
            job_file = "slurm-het.py"
            command = f"sbatch {' '.join(sbatch_args)} {job_file}"
            pshell.run(command)