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
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

pshell.run("export LCI_LOG_LEVEL=info")
pshell.run("export LCT_LOG_LEVEL=info")
# pshell.run("export LCI_OFI_PROVIDER_HINT=\"udp\"")
# pshell.run("export HPX_LCI_LOG_LEVEL=debug")
# pshell.run("export LCT_PMI_BACKEND=pmi2")
# pshell.run("export LCT_PCOUNTER_MODE=on-the-fly")
# pshell.run("export LCT_PCOUNTER_AUTO_DUMP=stderr")
# pshell.run("ulimit -c unlimited")
# pshell.run("export LCI_ENABLE_PRG_NET_ENDPOINT=0")
# pshell.run("export LCI_PAPI_EVENTS=PAPI_FP_OPS")
# pshell.run("export FI_LOG_LEVEL=warn")
# pshell.run("export FI_LOG_PROV=cxi")
# pshell.run("export MPIR_CVAR_CH4_NUM_VCIS=10")
# pshell.run("export UCX_TLS=rc,self")

start_time = time.time()
for config in configs:
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