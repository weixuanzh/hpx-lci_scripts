def get_platform_config_all():
    return {
        "name": "delta",
        "core_num": 128,
        "numa_policy": None,
        "account": "bbqm-delta-cpu",
        "partition": "cpu",
        "octotiger_major": "master"
    }

def get_srun_pmi_option(config):
    srun_pmi_option = ""
    return srun_pmi_option