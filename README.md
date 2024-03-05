# HPX/LCI Scripts

### Overview

This is a scripts collection for running HPX/LCI related software on clusters.
All scripts are written in Python (including those that will be submitted to
SLURM). The execution environment are managed by Spack environment.

### File Structure
- include: common python scripts imported by others
  - platforms: platform-specific configurations.
- spack_env/<platform_name>/<env_name>: spack environment yaml file
- lci: Scripts to run LCI software.
- hpx: Scripts to run HPX software.
- hpx_pingpong: Scripts to run the HPX Ping-pong benchmark.
- octotiger: Scripts to run Octo-Tiger.

Within the lci/hpx/hpx_pingpong_octotiger directory, there are a number of
subdirectories, such as "benchmark", "debug", "perf", serving different
purposes. Within each subdirectory, you may find the following scripts:
- run.py: the script that submit one or more jobs to platforms (typically
          through SLRUM `sbatch`).
- slurm.py: the script that `run.py` submit to the platforms. Users generally
            should not run this script directly.
- parse.py: the script that parse the experiment results from log file 
            into `csv` file.
- draw.py: the script that plot the experiment results from the `csv` file.

### A typical workflow
Suppose we are on Perlmutter and want to run Octo-Tiger benchmarks.

Setup phase:
1. `spack environment activate path/to/hpx-lci_scripts/spack_env/perlmutter/hpx-lcw`:
   activate the spack environment we want to use.
2. `spack concretize ; spack install`: install the environment.

Experiment phase:
1. `cd path/to/hpx-lci_scripts/octotiger/benchmark`
2. `vim run.py`: decide which configurations I want to run
3. `run.py 5`: run all configurations 5 times.
4. `parse.py`: (After all jobs complete) parse all SLURM output files.
5. `draw.py`: plot the results.

### Important notes on how the scripts work
#### Persistent shell
Using python to run shell command can be difficult, because the environment 
or current path does not persist through multiple `subprocess` or `os.system`
calls. For example, the following python code will not work
```
os.system("module load openmpi")
os.system("export DEBUG_MODE=1")
os.system("cd workspace/hello_world")
os.system("mpirun -n 2 hello_world")
```
As a result, all shell commands invoked by the python scripts in this project
are all through the special [pshell](include/pshell.py) (persistent shell) module.
The following python code will work
```
pshell.run("module load openmpi")
pshell.run("export DEBUG_MODE=1")
pshell.run("cd workspace/hello_world")
pshell.run("mpirun -n 2 hello_world")
```