from script_common_lci import *

def get_lcw_environ_setting(config):
    ret = get_lci_environ_setting(config)
    if "lcw_backend" in config:
        ret["LCW_BACKEND_AUTO"] = config["lcw_backend"]
    return ret
