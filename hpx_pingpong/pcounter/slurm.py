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

def get_hpx_pingpong_args(config):
    args = []
    args = append_config_if_exist(args, "--nsteps={}", config, "nsteps")
    args = append_config_if_exist(args, "--nchains={}", config, "nchains")
    args = append_config_if_exist(args, "--nbytes={}", config, "nbytes")
    args = append_config_if_exist(args, "--intensity={}", config, "intensity")
    args = append_config_if_exist(args, "--is-single-source={}", config, "is_single_source")
    args = append_config_if_exist(args, "--enable-comp-timer={}", config, "enable_comp_timer")
    return ["pingpong_performance2"] + args + get_hpx_args(config)

# pshell.run("export MPIR_CVAR_CH4_NUM_VCIS=20")
# pshell.run("export UCX_TLS=rc,self")
pshell.run("cd " + os.path.join(current_path, "run"))
pshell.run("export LCT_PCOUNTER_MODE=on-the-fly")
pshell.run("export LCT_PCOUNTER_RECORD_INTERVAL=1000")
pshell.run("export LCT_PCOUNTER_AUTO_DUMP=lct_pcounter.{}.%.out".format(os.environ["SLURM_JOB_ID"]))

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    pshell.update_env(get_hpx_environ_setting(config))

    cmd = (get_platform_config("get_srun_args", config) +
           get_platform_config("get_numactl_args", config) +
           get_hpx_pingpong_args(config) + ["--batch-size=100"])
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))