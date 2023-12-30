import sys
sys.path.append("../../include")
from platform_config_base import *

class DeltaConfig(PlatformConfigBase):
    name = "delta"
    network = "ofi"
    cpus_per_node = 128
    gpus_per_node = 0
    cpus_per_core = 1
    numa_policy = "default"
    account = "bbqm-delta-cpu"
    partition = "cpu"
    qos = None
    scenarios_path = {
        "rs": "%root%/octotiger/data",
        "dwd-l10-beginning": "/scratch/bbqm/jiakuny/octotiger/q07_l10/beginning",
        "dwd-l10-close_to_merger": "/scratch/bbqm/jiakuny/octotiger/q07_l10/close_to_merger",
        "dwd-l11-beginning": "/scratch/bbqm/jiakuny/octotiger/q07_l11/beginning",
        "dwd-l11-close_to_merger": "/scratch/bbqm/jiakuny/octotiger/q07_l11/close_to_merger"
    }

    @property
    def additional_sbatch_args(self):
        return []

    def get_srun_pmi_args(self, config):
        return []

