from platform_config_base import *
from script_common import *
def get_lci_environ_setting(config):
    ret = {
        "LCI_SERVER_MAX_SENDS": "64",
        "LCI_SERVER_MAX_RECVS": "4096",
        "LCI_SERVER_NUM_PKTS": "65536",
        "LCI_SERVER_MAX_CQES": "65536",
        "LCI_PACKET_SIZE": "12288",
    }
    ret.update(get_platform_config("custom_env", config))
    if "match_table_type" in config:
        ret["LCI_MT_BACKEND"] = config["match_table_type"]
    if "cq_type" in config:
        ret["LCI_CQ_TYPE"] = config["cq_type"]
    if "mem_reg_cache" in config:
        ret["LCI_USE_DREG"] = str(config["mem_reg_cache"])
    if "lock_mode" in config:
        ret["LCI_BACKEND_TRY_LOCK_MODE"] = str(config["lock_mode"])
    if get_platform_config("network", config) == "ss11":
        ret["LCI_USE_DREG"] = 0
        ret["LCI_ENABLE_PRG_NET_ENDPOINT"] = 0
    return ret