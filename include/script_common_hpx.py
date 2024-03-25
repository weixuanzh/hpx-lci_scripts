from script_common_lcw import *

def get_hpx_environ_setting(config):
    ret = get_lci_environ_setting(config)
    if "reg_mem" in config and config["reg_mem"] or config["progress_type"] == "worker":
        # We only use the registration cache when only one progress thread is doing the registration.
        ret["LCI_USE_DREG"] = "0"
    return ret

def get_hpx_args(config):
    def append_pp_config_if_exist(args, arg, config, key, parcelports):
        if key in config and config["parcelport"] in parcelports:
            args.append(arg.format(config["parcelport"], config[key]))
        return args
    args = [
        "--hpx:ini=hpx.stacks.use_guard_pages=0",
        f"--hpx:ini=hpx.parcel.{config['parcelport']}.priority=1000",
    ]
    nthreads_default = int(platformConfig.cpus_per_node / platformConfig.cpus_per_core / get_config(config, 'ntasks_per_node', 1))
    nthreads = get_config(config, "nthreads", nthreads_default)
    args.append(f"--hpx:threads={nthreads}")

    args = append_config_if_exist(args, "--hpx:ini=hpx.agas.use_caching={}", config, "agas_caching")
    args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.zero_copy_receive_optimization={}", config,
                                  "zero_copy_recv")
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.zero_copy_serialization_threshold={}",
                                     config, "zc_threshold", ["mpi", "lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.sendimm={}", config,
                                     "sendimm", ["mpi", "lci", "lcw"])
    if "prg_thread_num" in config:
        if config["prg_thread_num"] == "auto":
            config["prg_thread_num"] = config["ndevices"]
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.protocol={}", config,
                                     "protocol", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.comp_type_header={}", config,
                                     "comp_type_header", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.comp_type_followup={}", config,
                                     "comp_type_followup", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.prepost_recv_num={}", config,
                                     "prepost_recv_num", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.reg_mem={}", config,
                                     "reg_mem", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.enable_in_buffer_assembly={}", config,
                                     "in_buffer_assembly", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.prg_thread_num={}", config,
                                     "prg_thread_num", ["lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.progress_type={}", config,
                                     "progress_type", ["lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.backlog_queue={}", config,
                                     "backlog_queue", ["lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.ndevices={}", config,
                                     "ndevices", ["lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.ncomps={}", config,
                                     "ncomps", ["lci", "lcw"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.send_nb_max_retry={}", config,
                                     "send_nb_max_retry", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.mbuffer_alloc_max_retry={}", config,
                                     "mbuffer_alloc_max_retry", ["lci"])
    args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.bg_work_when_send={}", config,
                                     "bg_work_when_send", ["lci"])
    return args