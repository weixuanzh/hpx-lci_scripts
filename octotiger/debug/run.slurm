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
export LCI_SERVER_MAX_SENDS=1024
export LCI_SERVER_MAX_RECVS=4096
export LCI_SERVER_NUM_PKTS=65536
export LCI_SERVER_MAX_CQES=65536
export LCI_PACKET_SIZE=12288
export LCI_MT_BACKEND=hashqueue
export LCI_CQ_TYPE=array_atomic_faa
export LCI_USE_DREG=0
export LCI_LOG_LEVEL=trace
cd /global/cfs/cdirs/xpress/operation_bell/jiakuny/octotiger/q07_l10/close_to_merger
srun octotiger --hpx:ini=hpx.stacks.use_guard_pages=0 --hpx:ini=hpx.parcel.lci.priority=1000 --disable_output=on \
     --amr_boundary_kernel_type=AMR_OPTIMIZED --hpx:threads=16 --config_file=dwd.ini --number_gpus=1 \
     --executors_per_gpu=128 --max_gpu_executor_queue_length=1 --monopole_host_kernel_type=DEVICE_ONLY \
     --multipole_host_kernel_type=DEVICE_ONLY --hydro_host_kernel_type=DEVICE_ONLY --monopole_device_kernel_type=CUDA \
     --multipole_device_kernel_type=CUDA --hydro_device_kernel_type=CUDA --stop_step=10 \
     --hpx:ini=hpx.parcel.lci.zero_copy_serialization_threshold=8192 --hpx:ini=hpx.parcel.lci.sendimm=1 \
     --hpx:ini=hpx.parcel.zero_copy_receive_optimization=1 --hpx:ini=hpx.parcel.lci.prg_thread_num=1 \
     --hpx:ini=hpx.parcel.lci.protocol=putsendrecv --hpx:ini=hpx.parcel.lci.comp_type=queue \
     --hpx:ini=hpx.parcel.lci.progress_type=worker --hpx:ini=hpx.parcel.lci.backlog_queue=0 \
     --hpx:ini=hpx.parcel.lci.prepost_recv_num=1 --hpx:ini=hpx.parcel.lci.reg_mem=1 \
     --hpx:ini=hpx.parcel.lci.ndevices=1 --hpx:ini=hpx.parcel.lci.ncomps=1 \
     --hpx:ini=hpx.parcel.lci.enable_in_buffer_assembly=1 --hpx:ini=hpx.parcel.lci.log_level=debug
