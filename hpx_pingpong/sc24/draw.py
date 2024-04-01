import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import itertools
sys.path.append("../../include")
from draw_simple import *
from draw_bokeh import plot_bokeh
import numpy as np
import re
import math

job_name = "20240331-delta"
input_path = "data/"
output_path = "draw/"

def plot(df, x_key, y_key, tag_key, title,
         x_label=None, y_label=None,
         dirname=None, filename=None,
         label_fn=None, zero_x_is=0,
         base=None, smaller_is_better=True,
         with_error=True, position="all"):
    plot_bokeh(df, x_key, y_key, tag_key, title,
               x_label=x_label, y_label=y_label,
               dirname=dirname, filename=filename,
               label_fn=label_fn, zero_x_is=zero_x_is)
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[tag_key, x_key])
    lines = parse_tag(df, x_key, y_key, tag_key)

    # fig, ax = plt.subplots(figsize=(4.8, 3.6))
    # update labels
    if label_fn is not None:
        for line in lines:
            line["label"] = label_fn(line["label"])
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    fig, ax = plt.subplots()
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

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines, "Speedup": speedup_lines}, outfile)

def plot_bars(df, x_key, y_key, title,
              x_label=None, y_label=None,
              dirname=None, filename=None):
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[x_key])
    data = parse_simple(df, x_key, y_key)

    fig, ax = plt.subplots()
    bar = ax.barh(data["x"], data["y"], xerr=data["error"], label=y_label)
    ax.barh(data["x"], np.array(data["y"]) * 0.08, left=data["y"], color="white")
    for i, rect in enumerate(bar):
        text = f'{data["y"][i]:.2f}'
        ax.text(data["y"][i], rect.get_y() + rect.get_height() / 2.0,
                text, ha='left', va='center')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if filename is None:
        filename = title

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}-bar.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')

def batch(df):
    dirname = os.path.join(output_path, job_name)

    # df["name"] = df.apply(lambda row: (row["parcelport"] + "_i") if row["sendimm"] else row["parcelport"], axis=1)

    ## lines
    # flood
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["nchains"] == 1000000 and
                          row["nsteps"] == 1 and
                          row["name"] in ["mpi", "lci", "mpi_a"] and
                          row["pingpong_config_name"] == "flood",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nthreads", "msg_rate(K/s)", "name", None,
         dirname=dirname, filename="flood-8b", base="lci", smaller_is_better=False, with_error=True,
         x_label="Thread Number", y_label="Message Rate (K/s)")

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nchains"] >= 10000 and
                          row["nsteps"] == 1 and
                          row["name"] in ["mpi", "lci", "mpi_a"] and
                          row["pingpong_config_name"] == "flood",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nthreads", "msg_rate(K/s)", "name", None,
         dirname=dirname, filename="flood-16kb", base="lci", smaller_is_better=False, with_error=True,
         x_label="Thread Number", y_label="Message Rate (K/s)")

    # # nbytes
    # df1_tmp = df[df.apply(lambda row:
    #                       row["nchains"] == 1024 and
    #                       row["intensity"] == 0 and
    #                       row["name"] in ["mpi", "lci", "mpi_a"] and
    #                       row["pingpong_config_name"] == "nbytes",
    #                       axis=1)]
    # df1 = df1_tmp.copy()
    # plot(df1, "nbytes", "latency(us)", "name", None,
    #      dirname=dirname, filename="nbytes", base="lci", smaller_is_better=True, with_error=True,
    #      x_label="nbytes", y_label="Latency (us)")

    # nchains
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["intensity"] == 0 and
                          row["name"] in ["mpi", "lci", "mpi_a"] and
                          row["pingpong_config_name"] == "nchains",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nchains", "latency(us)", "name", None,
         dirname=dirname, filename="nchains-8b", base="lci", smaller_is_better=True, with_error=True,
         x_label="nchains", y_label="Latency (us)")

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["intensity"] == 0 and
                          row["name"] in ["mpi", "lci", "mpi_a"] and
                          row["pingpong_config_name"] == "nchains",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nchains", "latency(us)", "name", None,
         dirname=dirname, filename="nchains-16kb", base="lci", smaller_is_better=True, with_error=True,
         x_label="nchains", y_label="Latency (us)")

    # # computation
    # df1_tmp = df[df.apply(lambda row:
    #                       row["nbytes"] == 16384 and
    #                       row["nchains"] == 1024 and
    #                       row["name"] in ["mpi", "lci", "mpi_a"] and
    #                       row["pingpong_config_name"] == "comp",
    #                       axis=1)]
    # df1 = df1_tmp.copy()
    # plot(df1, "task_comp_time", "efficiency", "name", None,
    #      dirname=dirname, filename="comp_efficiency", base="lci", smaller_is_better=False, with_error=True,
    #      x_label="Computation(us)", y_label="Efficiency", zero_x_is=1)

    ## bars
    # df["nthreads"] = df.apply(lambda row: 128 if pd.isna(row["nthreads"]) else row["nthreads"], axis=1)
    # flood
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["nchains"] == 1000000 and
                          row["nsteps"] == 1 and
                          (row["nthreads"] == 128 or pd.isna(row["nthreads"])) and
                          row["pingpong_config_name"] == "flood",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot_bars(df1, "name", "msg_rate(K/s)", None,
         dirname=dirname, filename="flood-8b",
         x_label="Thread Number", y_label="Message Rate (K/s)")

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nchains"] >= 10000 and
                          row["nsteps"] == 1 and
                          (row["nthreads"] == 128 or pd.isna(row["nthreads"])) and
                          row["pingpong_config_name"] == "flood",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot_bars(df1, "name", "msg_rate(K/s)", None,
         dirname=dirname, filename="flood-16kb",
         x_label="Thread Number", y_label="Message Rate (K/s)")

    # nchains
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["intensity"] == 0 and
                          row["nchains"] == 1024 and
                          row["pingpong_config_name"] == "nchains",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot_bars(df1, "name", "latency(us)", None,
         dirname=dirname, filename="nchains-8b",
         x_label="nchains", y_label="Latency (us)")

    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["intensity"] == 0 and
                          row["nchains"] == 1024 and
                          row["pingpong_config_name"] == "nchains",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot_bars(df1, "name", "latency(us)", None,
         dirname=dirname, filename="nchains-16kb",
         x_label="nchains", y_label="Latency (us)")

    # # computation
    # df1_tmp = df[df.apply(lambda row:
    #                       row["nbytes"] == 16384 and
    #                       row["nchains"] == 1024 and
    #                       row["task_comp_time"] == 1000 and
    #                       row["pingpong_config_name"] == "comp",
    #                       axis=1)]
    # df1 = df1_tmp.copy()
    # plot_bars(df1, "name", "efficiency",  None,
    #      dirname=dirname, filename="comp_efficiency",
    #      x_label="Computation(us)", y_label="Efficiency")

if __name__ == "__main__":
    df = pd.read_csv(os.path.join(input_path, job_name + ".csv"))
    # interactive(df)
    batch(df)
