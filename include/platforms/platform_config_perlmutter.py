import sys
sys.path.append("../../include")
from platform_config_base import *
import pshell

class PerlmutterConfig(PlatformConfigBase):
    name = "perlmutter"
    network = "ss11"
    cpus_per_node = 128
    gpus_per_node = 4
    cpus_per_core = 2
    numa_policy = "default"
    account = "m4452"
    # account = "xpress"
    partition = None
    scenarios_path = {
        "rs": "%root%/octotiger/data",
        "dwd-l10-beginning": "/pscratch/sd/j/jackyan/octotiger/q07_l10/beginning",
        "dwd-l10-close_to_merger": "/pscratch/sd/j/jackyan/octotiger/q07_l10/close_to_merger",
        "dwd-l11-beginning": "/pscratch/sd/j/jackyan/octotiger/q07_l11/beginning",
        "dwd-l11-close_to_merger": "/pscratch/sd/j/jackyan/octotiger/q07_l11/close_to_merger",
        "dwd-l12-beginning": "/pscratch/sd/j/jackyan/octotiger/q07_l12/beginning",
        "dwd-l12-close_to_merger": "/pscratch/sd/j/jackyan/octotiger/q07_l12/close_to_merger",
    }

    def qos(self, config):
        nnodes = config["nnodes"]
        if nnodes <= 8:
            ret, _ = pshell.run(["squeue", "-u", os.environ["USER"]], to_print=False)
            count = ret.count("debug")
            if count <= 5:
                return "debug"
        return "regular"

    @property
    def additional_sbatch_args(self):
        return ["--constraint=\"gpu&hbm40g\""]

    def get_srun_args(self, config):
        return ["srun", "-l"]

    def custom_env(self, config):
        return {"PMI_MAX_KVS_ENTRIES": "65536"}

