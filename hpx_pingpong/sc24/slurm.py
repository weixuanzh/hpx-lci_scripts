#!/usr/bin/env python3
import os
import sys
import json
import time

# load root path
current_path = os.environ["CURRENT_PATH"]
root_path = os.path.realpath(os.path.join(current_path, "../.."))

sys.path.append(os.path.join(root_path, "include"))
import pshell
from script_common_hpx import *
from script_common import *

# load configuration
config_str = getenv_or("CONFIGS", None)
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]
pshell.run("export UCX_TLS=rc,self")
# pshell.run("export UCX_IB_REG_METHODS=direct")
pshell.run("export UCX_RNDV_THRESH=12288")
pshell.run("export UCX_MAX_RNDV_RAILS=1")
pshell.run("export UCX_BCOPY_THRESH=32")
pshell.run("export UCX_NET_DEVICES=mlx5_0:1")
pshell.run("export TCMALLOC_MAX_TOTAL_THREAD_CACHE_BYTES=1677721600")

def get_hpx_pingpong_args(config):
    args = []
    args = append_config_if_exist(args, "--nsteps={}", config, "nsteps")
    args = append_config_if_exist(args, "--nchains={}", config, "nchains")
    args = append_config_if_exist(args, "--nbytes={}", config, "nbytes")
    args = append_config_if_exist(args, "--intensity={}", config, "intensity")
    args = append_config_if_exist(args, "--is-single-source={}", config, "is_single_source")
    args = append_config_if_exist(args, "--task-comp-time={}", config, "task_comp_time")
    args = append_config_if_exist(args, "--batch-size={}", config, "batch_size")
    return ["pingpong_performance2"] + args + get_hpx_args(config)

start_time = time.time()
for i in range(5):
    for config in configs:
        print("Config: " + json.dumps(config))
        pshell.update_env(get_hpx_environ_setting(config))

        cmd = (get_platform_config("get_srun_args", config) +
               get_platform_config("get_numactl_args", config) +
               get_hpx_pingpong_args(config))
        if i == 0:
            # warmup
            pshell.run(cmd, to_print=False)
        pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))