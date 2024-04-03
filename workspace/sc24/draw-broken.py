import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import json
import itertools
import math
import re

from matplotlib import gridspec, ticker
from matplotlib.ticker import FormatStrFormatter

job_name = "20240330-brief"
job_name_dict = {
    "Expanse": {
        "mbench": "../../hpx_pingpong/sc24/data/20240330-expanse.csv",
        "bench": "../../octotiger/sc24/data/20240330-expanse.csv"
    },
    "Frontera": {
        "mbench": "../../hpx_pingpong/sc24/data/20240319-frontera.csv",
        "bench": "../../octotiger/sc24/data/20240320-frontera.csv"
    },
    "Delta": {
        "mbench": "../../hpx_pingpong/sc24/data/20240331-delta.csv",
        "bench": "../../octotiger/sc24/data/20240331-delta.csv"
    }
}
platform = ["Expanse", "Frontera"]
output_path = "draw/{}".format(job_name)
dirname = "config"
use_median = True
with_error = True

platform_config = {
    "Expanse": {
        "nnodes": 32,
        "nthreads": 128,
        "flood_16kb_nchains": 100000,
    },
    "Frontera": {
        "nnodes": 32,
        "nthreads": 56,
        "flood_16kb_nchains": 100000,
    },
    "Delta": {
        "nnodes": 32,
        "nthreads": 128,
        "flood_16kb_nchains": 10000,
    }
}


def parse_tag(df, x_key, y_key, tag_key):
    lines = []

    for tag in df[tag_key].unique():
        criterion = (df[tag_key] == tag)
        df1 = df[criterion]
        current_domain = []
        current_value = []
        current_error = []
        for x in df1[x_key].unique():
            y = df1[df1[x_key] == x].mean(numeric_only=True)[y_key]
            error = df1[df1[x_key] == x].std(numeric_only=True)[y_key]
            if y is np.nan:
                continue
            if y == 0:
                continue
            current_domain.append(float(x))
            current_value.append(float(y))
            if math.isnan(error):
                error = 0
            current_error.append(float(error))
        lines.append({'label': str(tag), 'x': current_domain, 'y': current_value, 'error': current_error})
    return lines

def preprocess_df(df):
    def rename_fn(x):
        if x["name"] == "lci_rp":
            return "lci_pin"
        else:
            return x["name"]

    df["name"] = df.apply(rename_fn, axis=1)

    def ndevice_tag_fn(x):
        if re.match("lci_mt_d\d+_c\d+", x["name"]):
            return "base"
        elif re.match("lci_global_d\d+", x["name"]):
            return "try-lock"
        elif re.match("lci_global_b_d\d+", x["name"]):
            return "lock"
        else:
            return None

    df["ndevices_tag"] = df.apply(ndevice_tag_fn, axis=1)
    return df

if __name__ == "__main__":
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14
    # df_mbench = preprocess_df(pd.read_csv(job_name_dict[platform]["mbench"]))
    # df_bench = preprocess_df(pd.read_csv(job_name_dict[platform]["bench"]))
    # df = (df_mbench, df_bench)
    # batch(df)

    platforms = ["Expanse", "Frontera"]
    dfs = []
    for platform in platforms:
        df = preprocess_df(pd.read_csv(job_name_dict[platform]["mbench"]))
        df["job"] = "hpx_pingpong"
        df["platform"] = platform
        dfs.append(df)
        df = preprocess_df(pd.read_csv(job_name_dict[platform]["bench"]))
        df["job"] = "octotiger"
        df["platform"] = platform
        dfs.append(df)
    df = pd.concat(dfs)

    x_key = "ndevices"
    y_key = "Total(s)"
    tag_key = "ndevices_tag"
    dirname = dirname
    filename = "ndevices-app-broken"
    x_label = "Device Number"
    y_label = "Time to Solution (s)"
    def sort_key(x):
        return {"base": 0, "try-lock": 1, "lock": 2}[x["label"]]
    def criteria_fn1(row):
        return (row["ndevices_tag"] in ["base", "try-lock", "lock"] and
                row["max_level"] == 5 and
                row["platform"] == platforms[0])
    def criteria_fn2(row):
        return (row["ndevices_tag"] in ["base", "try-lock", "lock"] and
                row["max_level"] == 5 and
                row["platform"] == platforms[1])

    lines_json = []
    fig = plt.figure(figsize=(9, 2.45))
    spec = gridspec.GridSpec(ncols=2, nrows=2,
                             width_ratios=[1, 1], wspace=0.15,
                             hspace=0.1, height_ratios=[1, 2])
    ax1 = fig.add_subplot(spec[0, 0])
    ax2 = fig.add_subplot(spec[1, 0])
    ax3 = fig.add_subplot(spec[:, 1])

    ### Left figure
    df1 = df[df.apply(criteria_fn1, axis=1)]
    df1 = df1.sort_values(x_key)
    lines1 = parse_tag(df1, x_key, y_key, tag_key)

    if sort_key:
        lines1.sort(key=sort_key)

    markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
    # time
    for line in lines1:
        print(line)
        line["marker"] = next(markers)
        ax2.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=line["marker"],
                     markerfacecolor='white', capsize=3, markersize=8, linewidth=2)
        ax1.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=line["marker"],
                     markerfacecolor='white', capsize=3, markersize=8, linewidth=0)
    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.yaxis.set_label_coords(-0.14, 0.8)
    ax2.set_xscale("log")
    ax1.set_xscale("log")
    ax2.set_yscale("log")
    ax1.set_yscale("log")
    ax1.set_title(platforms[0], fontsize=14)

    plt.rcParams['axes.formatter.min_exponent'] = 2
    ax1.yaxis.set_minor_locator(ticker.MaxNLocator(2))
    ax2.yaxis.set_minor_locator(ticker.MaxNLocator(3))

    ax2.set_ylim(2.8, 3.6)
    ax1.set_ylim(45, 49)
    ax1.spines.bottom.set_visible(False)
    ax2.spines.top.set_visible(False)
    # ax1.xaxis.tick_top()
    ax1.tick_params(axis='x', which='both',
                    bottom=False, top=False,
                    labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()
    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                  linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

    lines_json.append(lines1)

    ### Right figure
    df2 = df[df.apply(criteria_fn2, axis=1)]
    df2 = df2.sort_values(x_key)
    lines2 = parse_tag(df2, x_key, y_key, tag_key)

    if sort_key:
        lines2.sort(key=sort_key)

    markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
    # time
    for line in lines2:
        print(line)
        line["marker"] = next(markers)
        ax3.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=line["marker"],
                     markerfacecolor='white', capsize=3, markersize=8, linewidth=2)
    ax3.set_xlabel(x_label)
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_title(platforms[1], fontsize=14)
    lines_json.append(lines2)

    # ask matplotlib for the plotted objects and their labels
    lines, labels = ax3.get_legend_handles_labels()
    fig.legend(lines, labels, loc="center", bbox_to_anchor=(0.5, 1.05), ncols=5, fontsize=14)
    # plt.tight_layout()
    ### Save
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines_json}, outfile)
