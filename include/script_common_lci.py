from platform_config_base import *
def get_lci_environ_setting(config):
    ret = {
        "LCI_SERVER_MAX_SENDS": "1024",
        "LCI_SERVER_MAX_RECVS": "4096",
        "LCI_SERVER_NUM_PKTS": "65536",
        "LCI_SERVER_MAX_CQES": "65536",
        "LCI_PACKET_SIZE": "65536",
    }
    if "match_table_type" in config:
        ret["LCI_MT_BACKEND"] = config["match_table_type"]
    if "cq_type" in config:
        ret["LCI_CQ_TYPE"] = config["cq_type"]
    if "mem_reg_cache" in config:
        ret["LCI_USE_DREG"] = str(config["mem_reg_cache"])
    if get_platform_config("network", config) == "ss11":
        ret["LCI_USE_DREG"] = 0
    return ret