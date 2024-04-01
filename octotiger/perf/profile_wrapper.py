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

# pshell.run("export LCT_LOG_LEVEL=info")
# pshell.run("export LCI_LOG_LEVEL=info")
# pshell.run("export LCT_PMI_BACKEND=pmi1")
# pshell.run("ulimit -c unlimited")
# pshell.run("env | grep PMI")
pshell.run("export UCX_TLS=rc,self")
pshell.run("export UCX_IB_REG_METHODS=direct")
pshell.run("export UCX_RNDV_THRESH=12288")
pshell.run("export UCX_MAX_RNDV_RAILS=1")
pshell.run("export UCX_BCOPY_THRESH=32")
pshell.run("export UCX_NET_DEVICES=mlx5_0:1")

for config in configs:
    pshell.update_env(get_octotiger_environ_setting(config))
    scenario = "rs"
    if "scenario" in config:
        scenario = config["scenario"]
    scenarios_path = get_platform_config("scenarios_path", config)[scenario].replace("%root%", root_path)
    pshell.run(f"cd {scenarios_path}")

    perf_output = f'perf.data.{config["name"]}.{os.environ["SLURM_JOB_ID"]}.{os.environ["SLURM_PROCID"]}'
    perf_args = f"record --freq=100 --call-graph dwarf -q -o {perf_output}".split(" ")
    if "perf" in config and config["perf"] == "stat":
        perf_args = ["stat", "-e",
                     "faults,cache-misses,"
                     "ls_refills_from_sys.ls_mabresp_rmt_cache,"
                     "ls_refills_from_sys.ls_mabresp_rmt_dram"]

    cmd = (["perf"] + perf_args +
           get_platform_config("get_numactl_args", config) +
           get_octotiger_cmd(config))
    pshell.run(cmd)
    if "perf" not in config or config["perf"] == "record":
        os.rename(f"{scenarios_path}/{perf_output}", f"{current_path}/run/{perf_output}")