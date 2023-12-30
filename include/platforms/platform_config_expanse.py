import sys

sys.path.append("../../include")
from platform_config_base import *

class ExpanseConfig(PlatformConfigBase):
    name = "expanse"
    network = "ibv"
    cpus_per_node = 128
    gpus_per_node = 0
    numa_policy = "interleave"
    account = "uic193"
    partition = "compute"

    def get_srun_pmi_args(self, config):
        if config["parcelport"] == "lci":
            srun_pmi_option = ["--mpi=pmi2"]
        elif config["parcelport"] == "mpi":
            srun_pmi_option = ["--mpi=pmix"]
        else:
            print("Unknown parcelport type: " + config["parcelport"])
            exit(1)
        return srun_pmi_option

