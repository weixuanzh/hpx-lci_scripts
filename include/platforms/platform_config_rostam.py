import sys
sys.path.append("../../include")
from platform_config_base import *

class RostamConfig(PlatformConfigBase):
    name = "rostam"
    network = "ibv"
    cpus_per_node = 40
    gpus_per_node = 0
    numa_policy = "default"
    account = None
    partition = "medusa"
    scenarios_path = {
        "rs": "%root%/octotiger/data",
    }

    def get_srun_args(self, config):
        return ["srun", "--mpi=pmi2"]