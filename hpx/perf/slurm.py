#!/usr/bin/env python3
import os
import sys
import time
# load root path
current_path = os.environ["CURRENT_PATH"]
root_path = os.path.realpath(os.path.join(current_path, "../.."))

sys.path.append(os.path.join(root_path, "include"))
from script_common_octotiger import *
import json

# load configuration
config_str = getenv_or("CONFIGS", get_octotiger_default_config())
print(config_str)
config = json.loads(config_str)
print("Config: " + json.dumps(config))

start_time = time.time()
# pshell.run(f"cd {current_path}/run")
scenario = "rs"
cmd = (get_platform_config("get_srun_args", config) + ["-u"] +
       [f"{current_path}/profile_wrapper.py"])
pshell.run(cmd)
end_time = time.time()
print("Executed 1 configs. Total time is {}s.".format(end_time - start_time))