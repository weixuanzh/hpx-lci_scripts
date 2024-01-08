import sys
sys.path.append("../../include")
from platform_config_base import *
import pshell

class PolarisConfig(PlatformConfigBase):
    name = "polaris"
    scheduler = "pbs"
    network = "ss11"
    cpus_per_node = 64
    gpus_per_node = 4
    cpus_per_core = 2
    numa_policy = "default"
    account = "MPICH_MCS"
    additional_sbatch_args = ["-l filesystems=home:eagle"]
    scenarios_path = {
        "rs": "%root%/octotiger/data",
    }

    def partition(self, config):
        nnodes = config["nnodes"]
        if nnodes <= 2:
            ret, _ = pshell.run(["qstat", "-w", "-u", os.environ["USER"]], to_print=False)
            count = ret.count("debug")
            if count == 0:
                return "debug"
            else:
                return "preemptable"
        elif nnodes <= 10:
            ret, _ = pshell.run(["qstat", "-w", "-u", os.environ["USER"]], to_print=False)
            count = ret.count("debug-scaling")
            if count == 0:
                return "debug-scaling"
            else:
                return "preemptable"
        # if nnodes <= 10:
        #     return "preemptable"
        else:
            return "prod"

    def get_srun_args(self, config):
        return ["mpirun"]