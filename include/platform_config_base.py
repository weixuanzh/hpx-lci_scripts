import os, sys

class PlatformConfigBase:
    name = "None"
    network = "ibv"
    srun_pmi_option=[]
    cpus_per_node = 64
    gpus_per_node = 0
    cpus_per_core = 1
    numa_policy = "default"
    account = None
    partition = None

    @property
    def additional_sbatch_args(self):
        return []

from platforms.platform_config_expanse import ExpanseConfig
from platforms.platform_config_rostam import RostamConfig
from platforms.platform_config_perlmutter import PerlmutterConfig

platformConfig = PlatformConfigBase()

if "CMD_WLM_CLUSTER_NAME" in os.environ and os.environ["CMD_WLM_CLUSTER_NAME"] == "expanse" or \
        "SLURM_CLUSTER_NAME" in os.environ and os.environ["SLURM_CLUSTER_NAME"] == "expanse":
    platformConfig = ExpanseConfig()
elif "HOSTNAME" in os.environ and "rostam" in os.environ["HOSTNAME"] or \
        "SLURM_CLUSTER_NAME" in os.environ and os.environ["SLURM_CLUSTER_NAME"] == "rostam":
    platformConfig = RostamConfig()
elif "NERSC_HOST" in os.environ and "perlmutter" == os.environ["NERSC_HOST"]:
    platformConfig = PerlmutterConfig()
elif "HOSTNAME" in os.environ and "delta" in os.environ["HOSTNAME"] or \
        "SLURM_CLUSTER_NAME" in os.environ and os.environ["SLURM_CLUSTER_NAME"] == "delta":
    pass
# else:
#     print("Unknown platform!")
#     exit(1)

def get_platform_config():
    return platformConfig
