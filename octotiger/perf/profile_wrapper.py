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
# print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

if platformConfig.name == "perlmutter":
    pshell.run("export PMI_MAX_KVS_ENTRIES=1024")
    if config["progress_type"] == "rp":
        pshell.run("export LCI_BACKEND_TRY_LOCK_MODE=send")

# pshell.run("export LCT_LOG_LEVEL=info")
# pshell.run("export LCI_LOG_LEVEL=info")
# pshell.run("export LCT_PMI_BACKEND=pmi1")
# pshell.run("ulimit -c unlimited")
# pshell.run("env | grep PMI")

pshell.update_env(get_octotiger_environ_setting(config))
scenario = "rs"
if "scenario" in config:
    scenario = config["scenario"]
scenarios_path = get_platform_config("scenarios_path", config)[scenario].replace("%root%", root_path)
pshell.run(f"cd {scenarios_path}")

perf_output = f'perf.data.{config["name"]}.{os.environ["SLURM_JOB_ID"]}.{os.environ["SLURM_PROCID"]}'
cmd = (f"perf record --freq=100 --call-graph dwarf -q -o {perf_output}".split(" ") +
       get_platform_config("get_numactl_args", config) +
       get_octotiger_cmd(root_path, config))
pshell.run(cmd)
os.rename(f"{scenarios_path}/{perf_output}", f"{current_path}/run/{perf_output}")