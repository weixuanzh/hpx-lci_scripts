import sys
sys.path.append("../../include")
from platform_config_base import *

class RostamConfig(PlatformConfigBase):
    name = "rostam"
    network = "ibv"
    srun_pmi_option="--mpi=pmix"
    cpus_per_node = 40
    gpus_per_node = 0
    numa_policy = "default"
    account = None
    partition = "medusa"

# def get_platform_config_all():
#     return {
#         "name": "rostam",
#         "core_num": 40,
#         "numa_policy": "default",
#         "account": None,
#         "partition": "medusa",
#         "octotiger_major": "local",
#         "module_init_file": "/usr/share/lmod/lmod/init/env_modules_python.py"
#     }