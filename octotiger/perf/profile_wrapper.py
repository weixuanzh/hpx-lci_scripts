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
config = get_octotiger_default_config()
if len(sys.argv) > 2:
    config = json.loads(sys.argv[2])

pshell.update_env(get_environ_setting(config))
if platformConfig.name == "perlmutter":
    pshell.run("export PMI_MAX_KVS_ENTRIES=1024")
    if config["progress_type"] == "rp":
        pshell.run("export LCI_BACKEND_TRY_LOCK_MODE=send")

pshell.run(f"cd {root_path}/octotiger/data")
perf_output = f'perf.data.{config["name"]}.{os.environ["SLURM_JOB_ID"]}.{os.environ["SLURM_PROCID"]}'
numactl_cmd = []
if platformConfig.numa_policy == "interleave":
    numactl_cmd = ["numactl", "--interleave=all"]
cmd = (f"perf record --freq=100 --call-graph dwarf -q -o {perf_output}".split(" ") +
       numactl_cmd + get_octotiger_cmd(root_path, config) + ["1>&2"])
pshell.run(cmd)
os.rename(f"{root_path}/octotiger/data/{perf_output}", f"{current_path}/run/{perf_output}")