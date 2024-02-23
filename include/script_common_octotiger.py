from script_common import *
import pshell
from platform_config_base import *
from script_common_hpx import *

def get_octotiger_default_config():
    default_config = {
        "griddim": 8,
        "zc_threshold": 8192,
        "name": "lci",
        "scenario": "rs",
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


def get_octotiger_cmd(config):
    args = [
        "--disable_output=on",
        "--amr_boundary_kernel_type=AMR_OPTIMIZED",
    ]

    if config["scenario"] == "rs":
        config_filename = "rotating_star.ini"
    elif config["scenario"] == "gr":
        config_filename = "sphere.ini"
    elif "dwd" in config["scenario"]:
        config_filename = "dwd.ini"
    else:
        print("Unknown task!")
        exit(1)
    args.append(f"--config_file={config_filename}")

    if "dwd" not in config["scenario"]:
        args = append_config_if_exist(args, "--max_level={}", config, "max_level")
        args.append(f"--theta={get_theta(config)}")
        args.append("--correct_am_hydro=0")

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

    args = append_config_if_exist(args, "--stop_step={}", config, "stop_step")
    cmd = ["octotiger"] + args + get_hpx_args(config)
    return cmd


def get_octotiger_environ_setting(config):
    return get_hpx_environ_setting(config)

def run_octotiger(root_path, config, extra_arguments=None):
    if extra_arguments is None:
        extra_arguments = []
    pshell.update_env(get_octotiger_environ_setting(config))
    numactl_cmd = []
    if platformConfig.numa_policy == "interleave":
        numactl_cmd = ["numactl", "--interleave=all"]

    scenario = "rs"
    if "scenario" in config:
        scenario = config["scenario"]
    scenarios_path = get_platform_config("scenarios_path", config)[scenario].replace("%root%", root_path)
    pshell.run(f"cd {scenarios_path}")
    cmd = (get_platform_config("get_srun_args", config) +
           numactl_cmd +
           get_octotiger_cmd(config) +
           extra_arguments)
    cmd = " ".join(cmd)
    print(cmd)
    sys.stdout.flush()
    sys.stderr.flush()
    pshell.run(cmd)

if __name__ == "__main__":
    run_octotiger(".", get_octotiger_default_config())
