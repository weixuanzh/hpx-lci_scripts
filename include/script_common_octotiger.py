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
    prg_thread_num = 1
    if "prg_thread_num" in config:
        if config["prg_thread_num"] == "auto":
            prg_thread_num = config["ndevices"]
        else:
            prg_thread_num = config["prg_thread_num"]

    agas_use_caching = 0
    if "agas_caching" in config:
        agas_use_caching = config["agas_caching"]

    if config["task"] == "rs":
        config_filename = "rotating_star.ini"
    elif config["task"] == "gr":
        config_filename = "sphere.ini"
    else:
        print("Unknown task!")
        exit(1)

    stop_step = 5
    if "stop_step" in config:
        stop_step = config["stop_step"]

    device_args = []
    if platformConfig.gpus_per_node == 0:
        device_args += [
            "--monopole_host_kernel_type=LEGACY",
            "--multipole_host_kernel_type=LEGACY",
            "--hydro_host_kernel_type=LEGACY",
            "--monopole_device_kernel_type=OFF",
            "--multipole_device_kernel_type=OFF",
            "--hydro_device_kernel_type=OFF"
        ]
    else:
        device_args += [
            f"--number_gpus={platformConfig.gpus_per_node}",
            "--executors_per_gpu=128",
            "--max_gpu_executor_queue_length=1",
            "--monopole_host_kernel_type=DEVICE_ONLY",
            "--multipole_host_kernel_type=DEVICE_ONLY",
            "--hydro_host_kernel_type=DEVICE_ONLY",
            "--monopole_device_kernel_type=CUDA",
            "--multipole_device_kernel_type=CUDA",
            "--hydro_device_kernel_type=CUDA"
        ]

    cmd = f'''octotiger \
--hpx:ini=hpx.stacks.use_guard_pages=0 \
--hpx:ini=hpx.parcel.{config["parcelport"]}.priority=1000 \
--hpx:ini=hpx.parcel.{config["parcelport"]}.zero_copy_serialization_threshold={config["zc_threshold"]} \
--config_file={root_path}/octotiger/data/{config_filename} \
--max_level={config["max_level"]} \
--stop_step={stop_step} \
--theta={get_theta(config)} \
--correct_am_hydro=0 \
--disable_output=on \
f{' '.join(device_args)} \
--amr_boundary_kernel_type=AMR_OPTIMIZED \
--hpx:ini=hpx.agas.use_caching={agas_use_caching} \
--hpx:ini=hpx.parcel.lci.protocol={config["protocol"]} \
--hpx:ini=hpx.parcel.lci.comp_type={config["comp_type"]} \
--hpx:ini=hpx.parcel.lci.progress_type={config["progress_type"]} \
--hpx:ini=hpx.parcel.{config["parcelport"]}.sendimm={config["sendimm"]} \
--hpx:ini=hpx.parcel.lci.backlog_queue={config["backlog_queue"]} \
--hpx:ini=hpx.parcel.lci.prepost_recv_num={config["prepost_recv_num"]} \
--hpx:ini=hpx.parcel.zero_copy_receive_optimization={config["zero_copy_recv"]} \
--hpx:ini=hpx.parcel.lci.reg_mem={config["reg_mem"]} \
--hpx:ini=hpx.parcel.lci.ndevices={config["ndevices"]} \
--hpx:ini=hpx.parcel.lci.prg_thread_num={prg_thread_num} \
--hpx:ini=hpx.parcel.lci.ncomps={config["ncomps"]} \
--hpx:ini=hpx.parcel.lci.enable_in_buffer_assembly={config["in_buffer_assembly"]}'''
    return cmd


def run_octotiger(root_path, config, extra_arguments=""):
    os.environ.update(get_environ_setting(config))
    platform_config = get_platform_config()
    numactl_cmd = ""
    if platform_config.numa_policy == "interleave":
        numactl_cmd = "numactl --interleave=all"

    cmd = f'''
cd {root_path}/octotiger/data || exit 1
srun {platform_config.srun_pmi_option} {numactl_cmd} {get_octotiger_cmd(root_path, config)} {extra_arguments}'''
    print(cmd)
    sys.stdout.flush()
    sys.stderr.flush()
    pshell.run(cmd)
