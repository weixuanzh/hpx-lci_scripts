#!/bin/bash
#SBATCH -A xpress
#SBATCH -C gpu
#SBATCH -q debug
#SBATCH -t 00:03:00
#SBATCH -n 1
#SBATCH --output=run/test.%j.out
#SBATCH --error=run/test.%j.out
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --gpus-per-task=4

cd ../data
echo "activating spack"
spack env activate ../../spack_env/perlmutter/hpx-lci
echo "start running"
srun -n 1  octotiger --hpx:ini=hpx.stacks.use_guard_pages=0 --hpx:ini=hpx.parcel.mpi.priority=1000 \
 --hpx:ini=hpx.parcel.mpi.zero_copy_serialization_threshold=4096 \
 --config_file=/global/u1/j/jackyan/workspace/hpx-lci_scripts/octotiger/data/rotating_star.ini \
 --max_level=5 --stop_step=5 --theta=0.34 --correct_am_hydro=0 --disable_output=on --number_gpus=1 \
 --executors_per_gpu=128 --max_gpu_executor_queue_length=1 --monopole_host_kernel_type=DEVICE_ONLY \
 --multipole_host_kernel_type=DEVICE_ONLY --hydro_host_kernel_type=DEVICE_ONLY --monopole_device_kernel_type=CUDA \
 --multipole_device_kernel_type=CUDA --hydro_device_kernel_type=CUDA --amr_boundary_kernel_type=AMR_OPTIMIZED \
 --hpx:ini=hpx.agas.use_caching=0 --hpx:ini=hpx.parcel.mpi.sendimm=0 \
 --hpx:ini=hpx.parcel.zero_copy_receive_optimization=1 --hpx:threads=64