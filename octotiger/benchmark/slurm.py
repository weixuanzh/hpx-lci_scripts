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
from script_common_octotiger import *
from script_common import *

# load configuration
config_str = getenv_or("CONFIGS", get_octotiger_default_config())
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]

# pshell.run("export FI_CXI_RX_MATCH_MODE=software")
# pshell.run("export FI_CXI_DEFAULT_CQ_SIZE=263404")
# pshell.run("export FI_CXI_OFLOW_BUF_SIZE=12582912")
# pshell.run("export FI_CXI_CQ_FILL_PERCENT=20")
# pshell.run("export LCI_LOG_LEVEL=info")
# pshell.run("export LCT_LOG_LEVEL=info")
# pshell.run("ulimit -c unlimited")

pshell.run("export MPIR_CVAR_CH4_NUM_VCIS=10")
pshell.run("export UCX_TLS=rc,self")

start_time = time.time()
for config in configs:
    if config["progress_type"] == "rp":
        pshell.run("export LCI_BACKEND_TRY_LOCK_MODE=send")
    print("Config: " + json.dumps(config))
    pshell.update_env(get_octotiger_environ_setting(config))

    scenario = "rs"
    if "scenario" in config:
        scenario = config["scenario"]
    scenarios_path = get_platform_config("scenarios_path", config)[scenario].replace("%root%", root_path)
    pshell.run(f"cd {scenarios_path}")

    cmd = (get_platform_config("get_srun_args", config) + ["-u"] +
           get_platform_config("get_numactl_args", config) +
           get_octotiger_cmd(config))
    pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))