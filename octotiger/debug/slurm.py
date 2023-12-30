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
from script_common_octotiger import *

# load configuration
config = get_octotiger_default_config()
if len(sys.argv) > 2:
    config = json.loads(sys.argv[2])
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

if platformConfig.name == "perlmutter" or platformConfig.name == "delta":
    pshell.run("export FI_CXI_RX_MATCH_MODE=software")
    pshell.run("export PMI_MAX_KVS_ENTRIES=2048")
    if config["progress_type"] == "rp":
        pshell.run("export LCI_BACKEND_TRY_LOCK_MODE=send")
pshell.run("export LCI_LOG_LEVEL=info")
pshell.run("export LCT_LOG_LEVEL=info")
pshell.run("export LCI_OFI_PROVIDER_HINT=\"udp\"")
# pshell.run("export HPX_LCI_LOG_LEVEL=debug")
# pshell.run("export LCT_PMI_BACKEND=pmi2")
# pshell.run("export LCT_PCOUNTER_MODE=on-the-fly")
# pshell.run("export LCT_PCOUNTER_AUTO_DUMP=stderr")
pshell.run("ulimit -c unlimited")

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    run_octotiger(root_path, config, extra_arguments=["1>&2"])
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))