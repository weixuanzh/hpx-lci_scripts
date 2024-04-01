import os
import sys
import shutil
import copy
import glob
import json
import itertools
from platform_config_base import *
import pshell

def rm(dir):
    try:
        shutil.rmtree(dir)
        print(f"Directory {dir} has been deleted successfully.")
    except OSError as e:
        print(f"Error: {dir} : {e.strerror}")

def mv(source, destination):
    try:
        source_files = glob.glob(source)
        for file in source_files:
            destination_filename = destination
            if os.path.isdir(destination_filename):
                destination_filename = os.path.join(destination_filename, os.path.basename(file))
            shutil.move(file, destination_filename)
            print(f"Moved '{file}' to '{destination_filename}'")
    except FileNotFoundError:
        print(f"Error: '{source}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied while moving '{source}'.")
    except shutil.Error as e:
        print(f"Error: Failed to move '{source}' to '{destination}': {e}")

def mkdir_s(dir):
    if os.path.exists(dir):
        file_str = ""
        for (root, dirs, files) in os.walk(dir):
            for file in files:
                file_str += os.path.join(root, file) + "\n"
        prompt = (("{} directory exists with the following files:\n\n {}\n"
                  "Are you sure to remove it | continue with it | or abort? [r|c|A]")
                  .format(dir, file_str))
        print(prompt)
        x = input()
        if x == "r":
            print("Remove {}".format(dir))
            trash_dir = dir + ".trash"
            if os.path.exists(trash_dir):
                rm(trash_dir)
            mv(dir, trash_dir)
        elif x == "c":
            print("Continue with previous work")
        else:
            print("Abort")
            sys.exit(1)

    if not os.path.exists(dir):
        os.mkdir(dir)

def getenv_or(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default

def get_config(config, key, default):
    if key in config and config[key] is not None:
        return config[key]
    else:
        return default

def append_config_if_exist(args, arg, config, key):
    if key in config:
        args.append(arg.format(config[key]))
    return args

def get_current_script_path():
    if "CURRENT_SCRIPT_PATH" in os.environ:
        return os.environ["CURRENT_SCRIPT_PATH"]
    else:
        return os.path.realpath(sys.argv[0])

def get_module():
    init_file = get_platform_config("module_init_file")
    if init_file is None:
        module_home = os.environ["MODULESHOME"]
        module_init_file_path = os.path.join(module_home, "init", "*.py")
        init_files = glob.glob(module_init_file_path)
        if len(init_files) != 1:
            print("Cannot find init file {}".format(init_files))
        init_file = init_files[0]
    print("Load init file {}".format(init_file))
    dir_name = os.path.dirname(init_file)
    file_name = os.path.basename(init_file)
    name = os.path.splitext(file_name)[0]
    if dir_name not in sys.path:
        sys.path.insert(0, dir_name)
    module = getattr(__import__(name, fromlist=["module"]), "module")
    return module

def module_list():
    os.system("module list")

def spack_env_activate(env):
    _, ret_stderr = pshell.run("spack env activate {}".format(env), to_print=False)
    if ret_stderr:
        for line in ret_stderr.splitlines():
            if "setup-env.sh" in line:
                pshell.run(line.strip())
                _, ret_stderr = pshell.run("spack env activate {}".format(env))
                break
    if ret_stderr:
        print(ret_stderr)
    assert not ret_stderr
    # ret_stdout, _ = pshell.run("spack env activate --sh {}".format(env), to_print=False)
    # if ret_stdout:
    #     pshell.run(ret_stdout.replace("\n", " ").strip()[:-1], to_print=False)

def submit_pbs_job(job_file, tag, nnodes, configs, time, name, partition, qos, extra_args):
    common_config = intersect_dicts(configs)
    if name is None:
        name = common_config["name"]
    ntasks_per_node = 1
    if "ntasks_per_node" in common_config:
        ntasks_per_node = common_config["ntasks_per_node"]
    job_name="{}-n{}-t{}-{}".format(tag, nnodes, ntasks_per_node, name)
    output_filename = "./run/{}/".format(job_name)
    if not os.path.exists(output_filename):
        os.mkdir(output_filename)
    pbs_args = [f"-A {get_platform_config('account', common_config, partition)}",
                "-k doe",
                f"-l walltime={time}:00",
                f"-l select={nnodes}",
                f"-N {tag}-{name}",
                f"-q {get_platform_config('partition', common_config, partition)}",
                f"-o {output_filename}",
                f"-e {output_filename}",
                "-V",
                ]
    if get_platform_config("additional_sbatch_args", common_config, extra_args):
        pbs_args += get_platform_config("additional_sbatch_args", common_config, extra_args)
    command = ["qsub"] + pbs_args + [job_file]
    pshell.run(command)

def submit_slurm_job(job_file, tag, nnodes, configs, time, name, partition, qos, extra_args):
    common_config = intersect_dicts(configs)
    if name is None:
        name = common_config["name"]
    ntasks_per_node = 1
    if "ntasks_per_node" in common_config:
        ntasks_per_node = common_config["ntasks_per_node"]
    job_name="n{}-t{}-{}".format(nnodes, ntasks_per_node, name)
    output_filename = "./run/slurm_output.{}.%x.j%j.out".format(tag)
    sbatch_args = ["--export=ALL",
                   f"--nodes={nnodes}",
                   f"--job-name={job_name}",
                   f"--output={output_filename}",
                   f"--error={output_filename}",
                   f"--time={time}",
                   f"--ntasks-per-node={ntasks_per_node}",
                   f"--cpus-per-task={int(get_platform_config('cpus_per_node', common_config) / ntasks_per_node)}",
                   ]
    gpus_per_node = int(get_platform_config("gpus_per_node", common_config) / ntasks_per_node)
    if gpus_per_node:
        sbatch_args.append(f"--gpus-per-task={gpus_per_node}")
    if get_platform_config("account", common_config):
        sbatch_args.append("--account={}".format(get_platform_config("account", common_config)))
    if not partition:
        partition = get_platform_config("partition", common_config)
    if partition:
        sbatch_args.append("--partition={} ".format(partition))
    if not qos:
        qos = get_platform_config("qos", common_config)
    if qos:
        sbatch_args.append("--qos={} ".format(qos))
    sbatch_args += get_platform_config("additional_sbatch_args", common_config, [])
    if extra_args:
        sbatch_args += extra_args

    current_path = get_current_script_path()
    command = f"sbatch {' '.join(sbatch_args)} {job_file}"
    pshell.run(command)

def submit_job(job_file, tag, nnodes, configs, time=1, name=None, partition=None, qos=None, extra_args=None):
    common_config = intersect_dicts(configs)
    pshell.run("export CURRENT_PATH={}".format(get_current_script_path()))
    pshell.run("export CONFIGS=\'{}\'".format(json.dumps(configs)))
    scheduler = get_platform_config("scheduler", common_config, "slurm")
    if scheduler == "slurm":
        submit_slurm_job(job_file, tag, nnodes, configs, time, name, partition, qos, extra_args)
    elif scheduler == "pbs":
        submit_pbs_job(job_file, tag, nnodes, configs, time, name, partition, qos, extra_args)

def submit_jobs(configs, matrix_outside=None, matrix_inside=None, update_outside=None, update_inside=None, config_fn=None, tag=None, time=1, name=None, partition=None, qos=None, extra_args=None):
    if matrix_inside is None:
        matrix_inside = []
    if matrix_outside is None:
        matrix_outside = ["nnodes"]
    if update_inside is None:
        update_inside = []
    if tag is None:
        tag = getenv_or("RUN_TAG", "default")
    root_path = os.path.realpath(os.path.join(get_current_script_path(), "../.."))
    flat_configs = flatten_configs(configs, matrix_outside, matrix_inside, update_outside, update_inside, config_fn)
    current_spack_env = None
    for configs_outside in flat_configs:
        common_config = intersect_dicts(configs_outside)
        if current_spack_env != common_config["spack_env"]:
            spack_env_activate(os.path.join(root_path, "spack_env", platformConfig.name, common_config["spack_env"]))
            current_spack_env = common_config["spack_env"]
        # print(config)
        time_lb = get_platform_config("job_time_lb", common_config, 0)
        if time < time_lb:
            time = time_lb
        submit_job("slurm.py", tag, common_config["nnodes"], configs_outside, time=time, name=name, partition=partition, qos=qos, extra_args=extra_args)

def flatten_configs(configs, matrix_outside, matrix_inside, update_outside=None, update_inside=None, config_fn=None):
    if not update_outside:
        update_outside = [None]
    if not update_inside:
        update_inside = [None]
    configs_outside = []
    for config in configs:
        for update_outside_entry in update_outside:
            config1 = config.copy()
            if update_outside_entry:
                config1.update(update_outside_entry)
            valLists_outside = [config1[key_outside] for key_outside in matrix_outside]
            for comb_outside in itertools.product(*valLists_outside):
                config2 = {**config1, **dict(zip(matrix_outside, comb_outside))}
                configs_inside = []

                # inside loop
                for update_inside_entry in update_inside:
                    config3 = config2.copy()
                    if update_inside_entry:
                        config3.update(update_inside_entry)
                    valLists_inside = [config3[key_inside] for key_inside in matrix_inside]
                    for comb_inside in itertools.product(*valLists_inside):
                        result = {**config3,
                                  **dict(zip(matrix_inside, comb_inside))}
                        if config_fn is not None:
                            result = config_fn(result)
                        configs_inside.append(result)
                configs_outside.append(configs_inside)
    return configs_outside

def dict_product(base, dicts1, dicts2):
    ret = []
    for dict1 in dicts1:
        for dict2 in dicts2:
            result = base.copy()
            result.update(dict1)
            result.update(dict2)
            ret.append(result)
    return ret

def intersect_dicts(dicts):
    if type(dicts) is not list:
        return dicts
    common_keys = set.intersection(*map(set, dicts))
    return {k:dicts[0][k] for k in common_keys}

if __name__ == "__main__":
    spack_env_activate("hpx-lci")