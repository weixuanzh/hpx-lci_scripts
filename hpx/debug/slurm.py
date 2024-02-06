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
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

if platformConfig.name == "perlmutter":
    pshell.run("export PMI_MAX_KVS_ENTRIES=1024")
# pshell.run("export LCT_PCOUNTER_MODE=on-the-fly")
# pshell.run("export LCT_PCOUNTER_AUTO_DUMP=stderr")
# pshell.run("export LCT_PCOUNTER_RECORD_INTERVAL=10000000")

start_time = time.time()
for config in configs:
    pshell.update_env(get_hpx_environ_setting(config))

    cmd = (get_platform_config("get_srun_args", config) +
           get_platform_config("get_numactl_args", config) +
           config["args"] + get_hpx_args(config))
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))