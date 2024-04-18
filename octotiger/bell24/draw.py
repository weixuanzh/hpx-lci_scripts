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
import math

job_name = "20240410-perlmutter-final"
job_name = "20240413-frontier"
input_path = "data/"
output_path = "draw/"
all_labels = ["nnodes", "scenario", "job", "parcelport", "nthreads", "max_level", "tag", "Total(s)"]

def plot(df, x_key, y_key, tag_key, title,
         x_label=None, y_label=None,
         dirname=None, filename=None,
         label_fn=None, zero_x_is=0,
         base=None, smaller_is_better=True,
         with_error=True, position="all",
         style_map=None):
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
    # markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
    markers = itertools.cycle(('o', 'v'))
    # time
    for line in lines:
        marker = next(markers)
        line["marker"] = marker
        color = None
        linestyle = None
        if style_map is not None:
            style = style_map(line["label"])
            if "color" in style:
                color = style["color"]
            if "linestyle" in style:
                linestyle = style["linestyle"]
        if with_error:
            line["error"] = [0 if math.isnan(x) else x for x in line["error"]]
            ax.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=marker, markerfacecolor='white', capsize=3, markersize=8, linewidth=2, color=color, linestyle=linestyle)
        else:
            ax.plot(line["x"], line["y"], label=line["label"], marker=marker, markerfacecolor='white', markersize=8, linewidth=2, color=color, linestyle=linestyle)
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
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='best', ncol=1, fancybox=True)
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

def batch(df):
    dirname = os.path.join(output_path, job_name)

    def calculate_flops(row):
        dict = {
            "dwd-l10-beginning": 5.27503e11 * 25,
            "dwd-l10-close_to_merger": 1.68309e12 * 25,
            "dwd-l11-beginning": 1.10725e12 * 25,
            "dwd-l11-close_to_merger": 1.74806e13 * 25,
            "dwd-l12-beginning": 9.04417e12 * 25,
            "dwd-l12-close_to_merger": 1.07915e14 * 25,
        }
        return dict[row["scenario"]] / row["Total(s)"]
    df["tag"] = df.apply(lambda row: "{}-{}".format(row["scenario"][:7], row["parcelport"]), axis=1)
    df["flops"] = df.apply(calculate_flops, axis=1)
    def style_map(name):
        color_dict = {
            # "dwd-l10-beginning": "C1",
            "dwd-l10": "C0",
            # "dwd-l11-beginning": "C3",
            "dwd-l11": "C1",
            # "dwd-l12-beginning": "C5",
            "dwd-l12": "C2",
        }
        line_dict = {
            "lci": "solid",
            "mpi": "dashed"
        }
        return {"color": color_dict[name[:-4]], "linestyle": line_dict[name[-3:]]}

    df1_tmp = df[df.apply(lambda row:
                          row["nnodes"] >= 2 and
                          "beginning" not in row["scenario"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nnodes", "Total(s)", "tag", "MPI parcelport v.s. LCI parcelport",
         x_label="Node Number", y_label="Time to Solution (s)",
         dirname=dirname, filename="mpi_vs_lci_time", base="lci", with_error=False, style_map=style_map)
    df1_tmp = df[df.apply(lambda row:
                          row["nnodes"] >= 2 and
                          "beginning" not in row["scenario"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nnodes", "flops", "tag", "MPI parcelport v.s. LCI parcelport",
         x_label="Node Number", y_label="FLOP/s",
         dirname=dirname, filename="mpi_vs_lci_flops", base="lci", with_error=False, style_map=style_map)


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(input_path, job_name + ".csv"))
    # interactive(df)
    batch(df)
