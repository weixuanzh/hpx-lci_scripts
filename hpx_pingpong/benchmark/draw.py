import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import itertools
from itertools import chain
sys.path.append("../../include")
from draw_simple import *
import numpy as np
import math

job_name = "20240205-all"
input_path = "data/"
output_path = "draw/"
all_labels = ["name", "nbytes", "nchains", "intensity", "msg_rate(K/s)", "bandwidth(MB/s)"]

def plot(df, x_key, y_key, tag_key, title,
         filename = None, base = None, smaller_is_better = True, label_fn=None,
         with_error=True, x_label=None, y_label=None, position="all",
         zero_x_is=0):
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[tag_key, x_key])

    fig, ax = plt.subplots()
    # fig, ax = plt.subplots(figsize=(4.8, 3.6))
    lines = parse_tag(df, x_key, y_key, tag_key)
    # update labels
    if label_fn is not None:
        for line in lines:
            line["label"] = label_fn(line["label"])
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    # Setup colors
    # cmap_tab20=plt.get_cmap('tab20')
    # ax.set_prop_cycle(color=[cmap_tab20(i) for i in chain(range(0, 20, 2), range(1, 20, 2))])
    markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
    # time
    for line in lines:
        marker = next(markers)
        line["marker"] = marker
        if with_error:
            line["error"] = [0 if math.isnan(x) else x for x in line["error"]]
            ax.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=marker, markerfacecolor='white', capsize=3, markersize=8, linewidth=2)
        else:
            ax.plot(line["x"], line["y"], label=line["label"], marker=marker, markerfacecolor='white', markersize=8, linewidth=2)
    ax.set_xlabel(x_label)
    if position == "all" or position == "left":
        ax.set_ylabel(y_label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(title)
    # ax.legend(bbox_to_anchor = (1.05, 0.6))
    # ax.legend(bbox_to_anchor=(1.01, 1.01))

    # speedup
    baseline = None
    ax2 = None
    speedup_lines = None
    for line in lines:
        if base == line["label"]:
            baseline = line
            break
    if baseline:
        ax2 = ax.twinx()
        speedup_lines = []
        for line in lines:
            if line['label'] == baseline['label']:
                ax2.plot(line["x"], [1 for x in range(len(line["x"]))], linestyle='dotted')
                continue
            if smaller_is_better:
                speedup = [float(x) / float(b) for x, b in zip(line["y"], baseline["y"])]
                label = "{} / {}".format(line['label'], baseline['label'])
            else:
                speedup = [float(b) / float(x) for x, b in zip(line["y"], baseline["y"])]
                label = "{} / {}".format(baseline['label'], line['label'])
            speedup_lines.append({"label": line["label"], "x": line["x"], "y": speedup})
            ax2.plot(line["x"][:len(speedup)], speedup, label=label, marker=line["marker"], markerfacecolor='white', linestyle='dotted', markersize=8, linewidth=2)
        if position == "all" or position == "right":
            ax2.set_ylabel("Speedup")
    # ax2.legend()

    # ask matplotlib for the plotted objects and their labels
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
    if ax2:
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(0, 1.2), ncol=3, fancybox=True)
    else:
        ax.legend()
    ax.tick_params(axis='y', which='both')
    # ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    # ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))

    plt.tight_layout()

    if filename is None:
        filename = title

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, job_name)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines, "Speedup": speedup_lines}, outfile)

def batch(df):
    df["name"] = df.apply(lambda row: row["name"].split("-")[0], axis=1)
    df["nthreads"] = df.apply(lambda row: 128 if pd.isna(row["nthreads"]) else row["nthreads"], axis=1)

    # nbytes
    df1_tmp = df[df.apply(lambda row:
                          row["nchains"] == 1024 and
                          row["intensity"] == 0 and
                          row["nthreads"] == 128,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nbytes", "latency(us)", "name", None,
         filename="nbytes", base = "lci", smaller_is_better=True, with_error=True,
         x_label="nbytes", y_label="Latency (us)")

    # nchains
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["intensity"] == 0 and
                          row["nthreads"] == 128,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nchains", "latency(us)", "name", None,
         filename="nchains-8", base = "lci", smaller_is_better=True, with_error=True,
         x_label="nchains", y_label="Latency (us)")

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["intensity"] == 0 and
                          row["nthreads"] == 128,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nchains", "latency(us)", "name", None,
         filename="nchains-16384", base = "lci", smaller_is_better=True, with_error=True,
         x_label="nchains", y_label="Latency (us)")

    # intensity
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nchains"] == 1024 and
                          row["nthreads"] == 128,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "intensity", "latency(us)", "name", None,
         filename="intensity", base = "lci", smaller_is_better=True, with_error=True,
         x_label="intensity", y_label="Latency (us)", zero_x_is=1)

    # nthreads
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["nchains"] == row["nthreads"] * 8 and
                          row["intensity"] == 0,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nthreads", "latency(us)", "name", None,
         filename="nthreads-8", base = "lci", smaller_is_better=True, with_error=True,
         x_label="nthreads", y_label="Latency (us)", zero_x_is=1)

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nchains"] == row["nthreads"] * 8 and
                          row["intensity"] == 0,
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nthreads", "latency(us)", "name", None,
         filename="nthreads-16384", base = "lci", smaller_is_better=True, with_error=True,
         x_label="nthreads", y_label="Latency (us)", zero_x_is=1)

if __name__ == "__main__":
    df = pd.read_csv(os.path.join(input_path, job_name + ".csv"))
    # interactive(df)
    batch(df)
