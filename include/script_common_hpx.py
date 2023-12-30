from script_common_lci import *

def get_hpx_environ_setting(config):
    ret = get_lci_environ_setting(config)
    if "reg_mem" in config and config["reg_mem"] or config["progress_type"] == "worker":
        # We only use the registration cache when only one progress thread is doing the registration.
        ret["LCI_USE_DREG"] = "0"
    return ret