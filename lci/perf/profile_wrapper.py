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
assert len(configs) == 1

pshell.run("export LCW_BACKEND_AUTO=lci")

pshell.run("cd run")
for config in configs:
    pshell.update_env(get_lci_environ_setting(config))
    perf_output = f'perf.data.{config["name"]}.{os.environ["SLURM_JOB_ID"]}.{os.environ["SLURM_PROCID"]}'
    cmd = (f"perf record --freq=100 --call-graph dwarf -q -o {perf_output}".split(" ") +
           get_platform_config("get_numactl_args", config) +
           config["args"])
    pshell.run(cmd)
