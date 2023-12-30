#!/usr/bin/env python3
import os
import sys
import json
import time

# load root path
assert len(sys.argv) > 1
current_path = sys.argv[1]
root_path = os.path.realpath(os.path.join(current_path, "../.."))

sys.path.append(os.path.join(root_path, "include"))
import pshell
from platform_config_base import *
from script_common_lci import *

# load configuration
config = None
if len(sys.argv) > 2:
    config = json.loads(sys.argv[2])
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

if platformConfig.name == "perlmutter":
    pshell.run("export PMI_MAX_KVS_ENTRIES=1024")

start_time = time.time()
for config in configs:
    pshell.update_env(get_lci_environ_setting(config))

    cmd = (["srun", "-u"] +
           get_platform_config("get_srun_pmi_args", config) +
           get_platform_config("get_numactl_args", config) +
           config["args"])
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))