def get_platform_config_all():
    return {
        "name": "expanse",
        "core_num": 128,
        "numa_policy": "interleave",
        "account": "uic193",
        "partition": "compute",
        "octotiger_major": "local"
    }

def get_srun_pmi_option(config):
    srun_pmi_option = ""
    if config["parcelport"] == "lci":
        srun_pmi_option = "--mpi=pmi2"
    elif config["parcelport"] == "mpi":
        srun_pmi_option = "--mpi=pmix"
    else:
        print("Unknown parcelport type: " + config["parcelport"])
        exit(1)
    return srun_pmi_option