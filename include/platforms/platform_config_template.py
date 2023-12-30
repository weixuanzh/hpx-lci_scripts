def get_platform_config_all():
    return {
        "name": "template", # Platform name
        "core_num": 40, # How many cores per node
        "numa_policy": "default", # Which numa policy to use? (default or interleave)
        "account": None, # SLURM account to charge to run the job
        "partition": "template", # SLURM partition
        "octotiger_major": "master", # Which octotiger version to use
        # python module file to load if it is not in the default location
        "module_init_file": "/usr/share/lmod/lmod/init/env_modules_python.py"
    }

def get_srun_pmi_args(config):
    # Any additional srun option to use
    # You may need to pass --mpi=pmi2|pmix to specify the PMI backend
    return "--mpi=pmix"