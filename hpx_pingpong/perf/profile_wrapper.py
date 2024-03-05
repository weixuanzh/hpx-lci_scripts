#!/usr/bin/env python3
import fcntl
import inspect
import os
import resource
import sys
import time
# load root path
current_path = os.environ["CURRENT_PATH"]
root_path = os.path.realpath(os.path.join(current_path, "../.."))

sys.path.append(os.path.join(root_path, "include"))
import pshell
from script_common_octotiger import *
from script_common import *

# load configuration
config_str = getenv_or("CONFIGS", get_octotiger_default_config())
# print(config_str)
config = json.loads(config_str)
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]
assert len(configs) == 1

def get_hpx_pingpong_args(config):
    args = []
    args = append_config_if_exist(args, "--nsteps={}", config, "nsteps")
    args = append_config_if_exist(args, "--nchains={}", config, "nchains")
    args = append_config_if_exist(args, "--nbytes={}", config, "nbytes")
    args = append_config_if_exist(args, "--intensity={}", config, "intensity")
    args = append_config_if_exist(args, "--is-single-source={}", config, "is_single_source")
    args = append_config_if_exist(args, "--enable-comp-timer={}", config, "enable_comp_timer")
    return ["pingpong_performance2"] + args + get_hpx_args(config)

pshell.run("cd run")
# pshell.run("export LCI_LOG_LEVEL=info")
pshell.run("export FI_LOG_LEVEL=warn")
pshell.run("export FI_LOG_PROV=cxi")
pshell.run("export FI_CXI_RX_MATCH_MODE=software")
pshell.run("export LD_LIBRARY_PATH=/u/jiakuny/workspace/spack/opt/spack/linux-rhel8-zen3/gcc-11.4.0/gcc-12.3.0-6z74qxwlsdandmnyqmij3xt4peykm2q6/lib64/:/u/jiakuny/workspace/spack/opt/spack/linux-rhel8-zen3/gcc-11.4.0/gcc-12.3.0-6z74qxwlsdandmnyqmij3xt4peykm2q6/lib64/")

for config in configs:
    pshell.update_env(get_hpx_environ_setting(config))

    perf_output = f'perf.data.{config["name"]}.{os.environ["SLURM_JOB_ID"]}.{os.environ["SLURM_PROCID"]}'
    cmd = (f"perf record --freq=100 --call-graph dwarf -q -o {perf_output}".split(" ") +
           get_platform_config("get_numactl_args", config) +
           get_hpx_pingpong_args(config))
    pshell.run(cmd)
end_time = time.time()
