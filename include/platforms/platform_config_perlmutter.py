import sys
sys.path.append("../../include")
from platform_config_base import *

class PerlmutterConfig(PlatformConfigBase):
    name = "perlmutter"
    network = "ofi"
    cpus_per_node = 128
    gpus_per_node = 4
    cpus_per_core = 2
    numa_policy = "default"
    account = "m4452"
    partition = None
    qos = "regular"

    @property
    def additional_sbatch_args(self):
        return ["--constraint=gpu"]

    def get_srun_pmi_option(self, config):
        return []