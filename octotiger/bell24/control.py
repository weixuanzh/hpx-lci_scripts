import os

def update_cmd(cmd, config):
    if "SLURM_JOB_ID" in os.environ and os.environ["SLURM_JOB_ID"] == "23933561":
        print("I am testing my control2")
    return cmd