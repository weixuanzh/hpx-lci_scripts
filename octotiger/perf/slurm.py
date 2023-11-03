#!/usr/bin/env python3
import os
import sys
sys.path.append(f'{os.environ["HOME"]}/workspace/hpx-lci_scripts/include')
from script_common_octotiger import *
import json

# load root path
assert len(sys.argv) > 1
current_path = sys.argv[1]
root_path = os.path.realpath(os.path.join(current_path, "../.."))
# load configuration
config = get_default_config()
if len(sys.argv) > 2:
    config = json.loads(sys.argv[2])
print("Config: " + json.dumps(config))

pshell.run(f"cd {current_path}/run")
cmd = (["srun"] + platformConfig.srun_pmi_option +
       [f"{current_path}/profile_wrapper.py", current_path, f"'{json.dumps(config)}'"])
pshell.run(cmd)