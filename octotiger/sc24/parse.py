#!/usr/bin/env python3

import json
import re
import glob
import numpy as np
import ast
import pandas as pd
import os,sys

name = "20240320-frontera"
input_path = "run/{}/slurm_output.*".format(name)
output_path = "data/"
filename_pattern = {
    "format": "\S+slurm_output\.(\S+)\.n(\d+)-t\d+-(\S+)\.j\S+",
    "label": ["tag", "nnodes", "name"],
}

line_patterns = [
{
    "format": "Config: (.+)",
    "label": ["config"],
},
{
    "format": "(?:.+  |)Total: (\S+)",
    "label": ["Total(s)"]
},
{
    "format": "(?:.+  |)Computation: (\S+) \(\S+ %\)",
    "label": ["Computation(s)"]
},
{
    "format": "(?:.+  |)Regrid: (\S+) \(\S+ %\)",
    "label": ["Regrid(s)"]
}]
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
        m = re.match(filename_pattern["format"], filename)
        if m:
            current_data = [get_typed_value(x) for x in m.groups()]
            current_label = filename_pattern["label"]
            for label, data in zip(current_label, current_data):
                current_entry[label] = data
        else:
            print("Ignore {}".format(filename))
            continue

        matched_count = 0
        with open(filename) as f:
            for line in f.readlines():
                line = line.strip()
                for pattern in line_patterns:
                    m = re.match(pattern["format"], line)
                    if m:
                        current_data = [get_typed_value(x) for x in m.groups()]
                        current_label = pattern["label"]
                        for label, data in zip(current_label, current_data):
                            if label == "config":
                                if type(data) is list:
                                    continue
                                data.pop("nnodes")
                                current_entry.update(data)
                                matched_count += 1
                            else:
                                current_entry[label] = data
                                matched_count += 1
                        break

        if matched_count != len(line_patterns):
            print("{} not found!".format(filename))
        else:
            print(current_entry)
            new_df = pd.DataFrame(current_entry, columns=list(current_entry.keys()), index=[1])
            if df is None:
                df = new_df
            else:
                df = pd.concat([df, new_df], ignore_index=True)

    # df = df[all_labels]
    # df = df.sort_values(by=all_labels)

    def name_fn(row):
        if row["parcelport"] == "mpi" and row["sendimm"] == 0:
            return "mpi_a"
        elif row["parcelport"] == "mpi" and row["sendimm"] == 1:
            return "mpi"
        else:
            return row["name"]

    df["name"] = df.apply(name_fn, axis=1)

    if df.shape[0] == 0:
        print("Error! Get 0 entries!")
        exit(1)
    else:
        print("get {} entries".format(df.shape[0]))

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    df.to_csv(os.path.join(output_path, "{}.csv".format(name)))