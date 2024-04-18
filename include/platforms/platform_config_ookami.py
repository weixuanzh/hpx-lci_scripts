import sys

sys.path.append("../../include")
from platform_config_base import *

class OokamiConfig(PlatformConfigBase):
    name = "ookami"
    network = "ibv"
    cpus_per_node = 48
    gpus_per_node = 0
    numa_policy = "default"
    additional_sbatch_args = []
    scenarios_path = {
        "rs": "%root%/octotiger/data",
        "dwd-l10-beginning": "/lustre/scratch/jiakyan/octotiger/q07_l10/beginning",
        "dwd-l10-close_to_merger": "/lustre/scratch/jiakyan/octotiger/q07_l10/close_to_merger",
        "dwd-l11-beginning": "/lustre/scratch/jiakyan/octotiger/q07_l11/beginning",
        "dwd-l11-close_to_merger": "/lustre/scratch/jiakyan/octotiger/q07_l11/close_to_merger",
    }

    def partition(self, config):
        nnodes = config["nnodes"]
        if nnodes <= 32:
            return "short"
        elif nnodes <= 40:
            return "medium"
        elif nnodes <= 80:
            return "large"
        else:
            return "all-nodes"

    def get_srun_args(self, config):
        if "parcelport" not in config:
            srun_pmi_option = ["--mpi=pmi2"]
        elif config["parcelport"] == "lci":
            srun_pmi_option = ["--mpi=pmi2"]
        else:
            srun_pmi_option = ["--mpi=pmix"]
        return ["srun"] + srun_pmi_option

