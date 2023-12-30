import sys
sys.path.append("../../include")
from platform_config_base import *

class PolarisConfig(PlatformConfigBase):
    name = "polaris"
    scheduler = "pbs"
    network = "ss11"
    cpus_per_node = 64
    gpus_per_node = 4
    cpus_per_core = 2
    numa_policy = "default"
    account = "CSC250STPM09"
    additional_sbatch_args = ["-l filesystems=home:eagle"]

    def partition(self, config):
        nnodes = config["nnodes"]
        if nnodes <= 2:
            return "debug"
        elif nnodes <= 10:
            return "debug-scaling"
        else:
            return "prod"

    def get_srun_pmi_args(self, config):
        return []