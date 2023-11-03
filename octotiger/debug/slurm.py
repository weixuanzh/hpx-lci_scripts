#!/usr/bin/env python3
import os
import sys
sys.path.append("../../include")
import pshell
from script_common_octotiger import *
import json
import time

# load root path
assert len(sys.argv) > 1
current_path = sys.argv[1]
root_path = os.path.realpath(os.path.join(current_path, "../.."))
# load configuration
config = get_default_config()
if len(sys.argv) > 2:
    config = json.loads(sys.argv[2])
print("Config: " + json.dumps(config))

if type(config) is list:
    configs = config
else:
    configs = [config]

# os.environ["FI_CXI_RX_MATCH_MODE"] = "software"
# pshell.run("export LCI_ENABLE_PRG_NET_ENDPOINT=0")
# pshell.run("export LCI_LOG_LEVEL=trace")
pshell.run("ulimit -c unlimited")

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    run_octotiger(root_path, config, extra_arguments=["1>&2"])
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))