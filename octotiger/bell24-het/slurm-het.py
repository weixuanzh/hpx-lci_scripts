#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime

# load root path
current_path = os.environ["CURRENT_PATH"]
root_path = os.path.realpath(os.path.join(current_path, "../.."))

sys.path.append(os.path.join(root_path, "include"))
import pshell
from script_common_octotiger import *
from script_common import *

sys.path.append(current_path)
from control import update_cmd

# load configuration
config_str = getenv_or("CONFIGS", get_octotiger_default_config())
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]

# basic logging
jobid = "Unknown"
if "SLURM_JOB_ID" in os.environ:
    jobid = os.environ["SLURM_JOB_ID"]
print("Job {} Time {} Platform {}", jobid, datetime.now(), platformConfig.name)

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    pshell.update_env(get_octotiger_environ_setting(config))

    scenario = "rs"
    if "scenario" in config:
        scenario = config["scenario"]
    scenarios_path = get_platform_config("scenarios_path", config)[scenario].replace("%root%", root_path)
    pshell.run(f"cd {scenarios_path}")

    het_groups_args = []
    if "het_groups" in config:
        het_groups = config["het_groups"]
        if len(het_groups) > 1:
            het_groups_args = ["--het-group=0-{}".format(len(het_groups)-1)]
    cmd = (get_platform_config("get_srun_args", config) + het_groups_args +
           get_platform_config("get_numactl_args", config) +
           get_octotiger_cmd(config))
    update_cmd(cmd, config)
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))