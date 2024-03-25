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
from script_common_lcw import *
from script_common import *

# load configuration
config_str = getenv_or("CONFIGS", None)
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]

def get_lcw_pingpong_args(config):
    args = []
    args = append_config_if_exist(args, "--op={}", config, "op")
    args = append_config_if_exist(args, "--ndevices={}", config, "ndevices")
    args = append_config_if_exist(args, "--nthreads={}", config, "nthreads")
    args = append_config_if_exist(args, "--min-size={}", config, "min_size")
    args = append_config_if_exist(args, "--max-size={}", config, "max_size")
    args = append_config_if_exist(args, "--niters={}", config, "niters")
    args = append_config_if_exist(args, "--test-mode={}", config, "test_mode")
    args = append_config_if_exist(args, "--pin-thread={}", config, "pin_thread")
    args = append_config_if_exist(args, "--nprgthreads={}", config, "nprgthreads")
    return ["lcw_pingpong_mt"] + args

# pshell.run("export MPIR_CVAR_CH4_NUM_VCIS=20")
# pshell.run("export UCX_TLS=rc,self")

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    pshell.update_env(get_lcw_environ_setting(config))

    cmd = (get_platform_config("get_srun_args", config) +
           get_platform_config("get_numactl_args", config) +
           get_lcw_pingpong_args(config))
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))