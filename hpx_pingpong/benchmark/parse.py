import json
import re
import glob
import numpy as np
import ast
import pandas as pd
import os,sys

name = "20240205-all"
input_path = "run/{}/slurm_output.*".format(name)
output_path = "data/"
line_patterns = [
{
    "format": "Config: (.+)",
    "label": ["config"],
},
{
    "format": "latency\(us\)=(\S+)",
    "label": ["latency(us)"]
},
{
    "format": "inject_rate\(K/s\)=(\S+)",
    "label": ["inject_rate(K/s)"]
},
{
    "format": "msg_rate\(K/s\)=(\S+)",
    "label": ["msg_rate(K/s)"]
},
{
    "format": "bandwidth\(MB/s\)=(\S+)",
    "label": ["bandwidth(MB/s)"]
},]
all_labels = [y for x in line_patterns for y in x["label"]]

def get_typed_value(value):
    if value == '-nan':
        return np.nan
    try:
        typed_value = ast.literal_eval(value)
    except:
        typed_value = value
    return typed_value

if __name__ == "__main__":
    filenames = glob.glob(input_path)

    df = None
    state = "init"
    current_entry = dict()
    print("{} files in total".format(len(filenames)))
    for filename in filenames:
        current_entry = dict()

        with open(filename) as f:
            try:
                for line in f.readlines():
                    line = line.strip()
                    for i, pattern in enumerate(line_patterns):
                        m = re.match(pattern["format"], line)
                        if m:
                            if i == 0:
                                current_entry = {}

                            current_data = [get_typed_value(x) for x in m.groups()]
                            current_label = pattern["label"]
                            for label, data in zip(current_label, current_data):
                                if label == "config":
                                    current_entry.update(data)
                                else:
                                    current_entry[label] = data

                            if i == len(line_patterns) - 1:
                                print(current_entry)
                                new_df = pd.DataFrame(current_entry, columns=list(current_entry.keys()), index=[1])
                                if df is None:
                                    df = new_df
                                else:
                                    df = pd.concat([df, new_df], ignore_index=True)
            except:
                print("Error parsing file " + filename)

    df = df.sort_values(by=["name", "inject_rate(K/s)"])

    if df.shape[0] == 0:
        print("Error! Get 0 entries!")
        exit(1)
    else:
        print("get {} entries".format(df.shape[0]))
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    df.to_csv(os.path.join(output_path, "{}.csv".format(name)))