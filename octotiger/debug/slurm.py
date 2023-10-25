#!/usr/bin/env python3
import os
import sys
sys.path.append("../../include")
import pshell
from script_common_octotiger import *
import json
import time

# load configuration
config = get_default_config()
if len(sys.argv) > 1:
    config = json.loads(sys.argv[1])

if type(config) is list:
    configs = config
else:
    configs = [config]

# set path
current_path = get_current_script_path()
root_path = os.path.realpath(os.path.join(current_path, "../.."))

start_time = time.time()
for config in configs:
    print("Config: " + json.dumps(config))
    # load modules
    # extra = ["ucx"]
    # if "special_branch" in config:
    #     extra += ["hpx/" + config["special_branch"], "lci/local-release-safeprog"]
    #     print(extra)
    # load_module(config, build_type="release", enable_pcounter=False, extra=extra)
    # module_list()

    spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, config["spack_env"]))
    run_octotiger(root_path, config)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))