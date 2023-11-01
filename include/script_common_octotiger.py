from script_common import *
import pshell
from platform_config_base import *


def get_default_config():
    default_config = {
        "griddim": 8,
        "zc_threshold": 8192,
        "name": "lci",
        "task": "rs",
        "parcelport": "lci",
        "max_level": 6,
        "protocol": "putva",
        "comp_type": "queue",
        "progress_type": "rp",
        "sendimm": 1,
        "backlog_queue": 0,
        "prg_thread_core": -1,
        "prepost_recv_num": 1,
        "zero_copy_recv": 1,
        "in_buffer_assembly": 1,
        "match_table_type": "hashqueue",
        "cq_type": "array_atomic_faa",
        "reg_mem": 0,
        "ndevices": 1,
        "ncomps": 1
    }
    return default_config


def get_theta(config):
    griddim = config["griddim"]
    if griddim >= 5:
        theta = 0.34
    elif 3 <= griddim <= 4:
        theta = 0.51
    elif 1 <= griddim <= 2:
        theta = 1.01
    else:
        print("invalid griddim {}!".format(griddim))
        exit(1)
    return theta


def get_environ_setting(config):
    ret = {
        "LCI_SERVER_MAX_SENDS": "1024",
        "LCI_SERVER_MAX_RECVS": "4096",
        "LCI_SERVER_NUM_PKTS": "65536",
        "LCI_SERVER_MAX_CQES": "65536",
        "LCI_PACKET_SIZE": "12288",
    }
    if "match_table_type" in config:
        ret["LCI_MT_BACKEND"] = config["match_table_type"]
    if "cq_type" in config:
        ret["LCI_CQ_TYPE"] = config["cq_type"]
    if "reg_mem" in config and config["reg_mem"] or config["progress_type"] == "worker":
        # We only use the registration cache when only one progress thread is doing the registration.
        ret["LCI_USE_DREG"] = "0"
    if "mem_reg_cache" in config:
        ret["LCI_USE_DREG"] = str(config["mem_reg_cache"])
    return ret


def get_octotiger_cmd(root_path, config):

    def get_config(config, key, default):
        if key in config:
            return config[key]
        else:
            return default
    def append_config_if_exist(args, arg, config, key):
        if key in config:
            args.append(arg.format(config[key]))
        return args
    args = [
        "--hpx:ini=hpx.stacks.use_guard_pages=0",
        f"--hpx:ini=hpx.parcel.{config['parcelport']}.priority=1000",
        f"--max_level={config['max_level']}",
        f"--theta={get_theta(config)}",
        "--correct_am_hydro=0",
        "--disable_output=on",
        "--amr_boundary_kernel_type=AMR_OPTIMIZED",
        f"--hpx:threads={int(platformConfig.cpus_per_node / platformConfig.cpus_per_core / get_config(config, 'ntasks_per_node', 1))}"
    ]

    if config["task"] == "rs":
        config_filename = "rotating_star.ini"
    elif config["task"] == "gr":
        config_filename = "sphere.ini"
    else:
        print("Unknown task!")
        exit(1)
    args.append(f"--config_file={root_path}/octotiger/data/{config_filename}")

    ngpus_to_use = get_config(config, "ngpus", platformConfig.gpus_per_node)
    if ngpus_to_use == 0:
        args += [
            "--monopole_host_kernel_type=LEGACY",
            "--multipole_host_kernel_type=LEGACY",
            "--hydro_host_kernel_type=LEGACY",
            "--monopole_device_kernel_type=OFF",
            "--multipole_device_kernel_type=OFF",
            "--hydro_device_kernel_type=OFF"
        ]
    else:
        args += [
            f"--number_gpus={ngpus_to_use}",
            "--executors_per_gpu=128",
            "--max_gpu_executor_queue_length=1",
            "--monopole_host_kernel_type=DEVICE_ONLY",
            "--multipole_host_kernel_type=DEVICE_ONLY",
            "--hydro_host_kernel_type=DEVICE_ONLY",
            "--monopole_device_kernel_type=CUDA",
            "--multipole_device_kernel_type=CUDA",
            "--hydro_device_kernel_type=CUDA"
        ]

    args = append_config_if_exist(args, "--hpx:ini=hpx.agas.use_caching={}", config, "agas_caching")
    args = append_config_if_exist(args, "--stop_step={}", config, "stop_step")
    args = append_config_if_exist(args, "--hpx:ini=hpx.parcel." + config['parcelport'] +
                                  ".zero_copy_serialization_threshold={}", config, "zc_threshold")
    args = append_config_if_exist(args, "--hpx:ini=hpx.parcel." + config['parcelport'] +
                                  ".sendimm={}", config, "sendimm")
    args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.zero_copy_receive_optimization={}", config,
                                  "zero_copy_recv")
    if config["parcelport"] == "lci":
        if "prg_thread_num" in config:
            if config["prg_thread_num"] == "auto":
                prg_thread_num = config["ndevices"]
            else:
                prg_thread_num = config["prg_thread_num"]
            args.append(f"--hpx:ini=hpx.parcel.lci.prg_thread_num={prg_thread_num}")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.protocol={}", config, "protocol")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.comp_type={}", config, "comp_type")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.progress_type={}", config, "progress_type")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.backlog_queue={}", config, "backlog_queue")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.prepost_recv_num={}", config, "prepost_recv_num")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.reg_mem={}", config, "reg_mem")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.ndevices={}", config, "ndevices")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.ncomps={}", config, "ncomps")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.enable_in_buffer_assembly={}", config,
                                      "in_buffer_assembly")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.lci.log_level={}", config, "lcipp_log_level")


    cmd = ["octotiger"] + args
    return cmd


def run_octotiger(root_path, config, extra_arguments=None):
    if extra_arguments is None:
        extra_arguments = []
    pshell.update_env(get_environ_setting(config))
    numactl_cmd = []
    if platformConfig.numa_policy == "interleave":
        numactl_cmd = ["numactl", "--interleave=all"]

    pshell.run(f"cd {root_path}/octotiger/data")
    cmd = (["srun"] +
           platformConfig.srun_pmi_option +
           numactl_cmd +
           get_octotiger_cmd(root_path, config) +
           extra_arguments)
    cmd = " ".join(cmd)
    print(cmd)
    sys.stdout.flush()
    sys.stderr.flush()
    pshell.run(cmd)

if __name__ == "__main__":
    run_octotiger(".", get_default_config())
