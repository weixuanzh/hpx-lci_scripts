import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import json
import itertools
import math
import re

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
        "mbench": "../../hpx_pingpong/sc24/data/20240323-delta.csv",
        "bench": "../../octotiger/sc24/data/20240322-delta.csv"
    }
}
platforms = ["Expanse", "Frontera"]
output_path = "draw/{}".format(job_name)
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


def draw_line(dfs, x_key, y_key, tag_key,
              dirname="default", filename=None, base=None, smaller_is_better=True, label_dict=None,
              with_error=True, sort_key=None, x_label=None, y_label=None,
              xscale=None, yscale=None,
              x_key_fn=None, tag_key_fn=None, criteria_fn=None):
    if label_dict is None:
        label_dict = {}
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    lines_json = []
    speedups_json = []
    fig, axs = plt.subplots(1, len(platforms), figsize=(4 * len(platforms), 3))
    for ax, platform, df in zip(axs, platforms, dfs):
        df = df.copy()
        if x_key_fn:
            df[x_key] = df.apply(x_key_fn, axis=1)
        if tag_key_fn:
            df[tag_key] = df.apply(tag_key_fn, axis=1)
        if criteria_fn:
            df = df[df.apply(criteria_fn, axis=1)]
        df = df.sort_values(x_key)

        lines = parse_tag(df, x_key, y_key, tag_key)
        # update labels
        if label_dict:
            for line in lines:
                label = line["label"]
                if label in label_dict:
                    line["label"] = label_dict[line["label"]]
            if base in label_dict:
                base = label_dict[base]

        if sort_key:
            lines.sort(key=sort_key)

        markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
        # time
        for line in lines:
            print(line)
            line["marker"] = next(markers)
            if with_error:
                ax.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=line["marker"],
                            markerfacecolor='white', capsize=3, markersize=8, linewidth=2)
            else:
                ax.plot(line["x"], line["y"], label=line["label"], marker=line["marker"], markerfacecolor='white',
                        markersize=8, linewidth=2)
        ax.set_xlabel(x_label, fontsize=14)
        if platform == platforms[0]:
            ax.set_ylabel(y_label, fontsize=14)
        ax.set_title(platform, fontsize=14)
        if xscale:
            ax.set_xscale(xscale)
        if yscale:
            ax.set_yscale(yscale)
        # ax.legend(bbox_to_anchor = (1.05, 0.6))
        # ax.legend()

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
                ax2.plot(line["x"][:len(speedup)], speedup, label=label, marker=line["marker"], markerfacecolor='white',
                         linestyle='dotted', markersize=8, linewidth=2)
            if platform == platforms[-1]:
                ax2.set_ylabel("Ratio", fontsize=14)
        # ax2.legend()
        plt.rcParams['axes.formatter.min_exponent'] = 2
        # ax.tick_params(axis='y', which='both')
        # ax.yaxis.set_minor_locator(ticker.MaxNLocator(2))
        # ax.yaxis.set_minor_formatter(ticker.LogFormatterMathtext())
        # ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))

        # ask matplotlib for the plotted objects and their labels
        if platform == platforms[0]:
            if ax2:
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                fig.legend(lines1 + lines2, labels1 + labels2, loc="center", bbox_to_anchor=(0.5, 1), ncols=5,
                           fontsize=14)
            else:
                fig.legend(loc="center", bbox_to_anchor=(0.5, 1), ncols=5, fontsize=14)

        lines_json.append(lines)
        speedups_json.append(speedup_lines)
    plt.tight_layout()

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines_json, "Ratio": speedups_json}, outfile)


def draw_bar(configs, dataset, labels, filename, dirname="default", title=None, legend_loc="best", legend_fn=None, with_error=True):
    if title is None:
        title = filename
    y = np.arange(len(labels))  # the label locations
    width = 1.0 / (len(configs) + 1)  # the width of the bars

    # fig, ax = plt.subplots()
    fig, axs = plt.subplots(1, len(platforms), figsize=(8, len(labels) * (len(configs) + 1) * 0.18 + 1))
    for ax, platform, data in zip(axs, platforms, dataset):
        hatches = itertools.cycle(["/", "\\", "|", "-", "+", "x", ".", "*", "o", "O"])
        for i in range(len(configs)):
            pos = y + width * (i + 0.5 - len(configs) / 2.0)
            legend = configs[i]
            if legend_fn:
                legend = legend_fn(legend)
            if with_error:
                bar = ax.barh(pos, data["xs"][i], width, xerr=data["stds"][i], label=legend, hatch=next(hatches))
            else:
                bar = ax.barh(pos, data["xs"][i], width, label=legend, hatch=next(hatches))
            ax.barh(pos, np.array(data["xs"][i]) * 0.08, width, left=data["xs"][i], color="white")
            for j, rect in enumerate(bar):
                text = f'{data["xs"][i][j]:.2f}'
                ax.text(data["xs"][i][j], rect.get_y() + rect.get_height() / 2.0,
                        text, ha='left', va='center')

        ax.set_yticks(y)
        if platform == platforms[0]:
            ax.set_yticklabels(labels)
            lines1, labels1 = ax.get_legend_handles_labels()
            nrows = math.ceil(len(labels1) / 4.0)
            ncols = len(labels1) / nrows
            if nrows == 1:
                y_loc = 1
            else:
                y_loc = 1.02
            fig.legend(lines1, labels1, loc="center", bbox_to_anchor=(0.5, y_loc), ncols=ncols)
        else:
            ax.set_yticklabels([])
        ax.set_title(platform)
        ax.set_xlabel("Normalized Performance")
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.grid(linestyle='dashed', axis="x")
    # plt.title(title)
    plt.tight_layout()

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump(list(zip(labels, dataset)), outfile)


def safe_loc(df, key, default=0.0):
    if key not in df or df.empty:
        return pd.Series([default])
    else:
        return df[key]


def extract_microbenchmark(df_mbench, name, platform, criteria_fn=None):
    df1_tmp = df_mbench[df_mbench.apply(lambda row:
                                        row["name"] == name and
                                        (not criteria_fn or criteria_fn(row)),
                                        axis=1)]
    message_rate_8b = safe_loc(df1_tmp[df1_tmp.apply(lambda row:
                                                     row["nbytes"] == 8 and
                                                     row["nchains"] == 1000000 and
                                                     row["nsteps"] == 1 and
                                                     (row["nthreads"] == platform_config[platform]["nthreads"]
                                                      or pd.isna(row["nthreads"])) and
                                                     row["pingpong_config_name"] == "flood",
                                                     axis=1)], "msg_rate(K/s)")
    message_rate_16kib = safe_loc(df1_tmp[df1_tmp.apply(lambda row:
                                                        row["nbytes"] == 16384 and
                                                        row["nchains"] == platform_config[platform][
                                                            "flood_16kb_nchains"] and
                                                        row["nsteps"] == 1 and
                                                        (row["nthreads"] == platform_config[platform]["nthreads"]
                                                         or pd.isna(row["nthreads"])) and
                                                        row["pingpong_config_name"] == "flood",
                                                        axis=1)], "msg_rate(K/s)")
    latency_8b = safe_loc(df1_tmp[df1_tmp.apply(lambda row:
                                                row["nbytes"] == 8 and
                                                row["intensity"] == 0 and
                                                row["nchains"] == 1024 and
                                                row["pingpong_config_name"] == "nchains",
                                                axis=1)], "latency(us)", np.inf).apply(lambda x: 1 / x)
    latency_16kib = safe_loc(df1_tmp[df1_tmp.apply(lambda row:
                                                   row["nbytes"] == 16384 and
                                                   row["intensity"] == 0 and
                                                   row["nchains"] == 1024 and
                                                   row["pingpong_config_name"] == "nchains",
                                                   axis=1)], "latency(us)", np.inf).apply(lambda x: 1 / x)
    efficiency = safe_loc(df1_tmp[df1_tmp.apply(lambda row:
                                                row["nbytes"] == 16384 and
                                                row["task_comp_time"] == 1000 and
                                                row["pingpong_config_name"] == "comp",
                                                axis=1)], "efficiency")
    return [message_rate_8b, message_rate_16kib, latency_8b, latency_16kib, efficiency]


def extract_benchmark(df_bench, name, platform, criteria_fn=None):
    total = safe_loc(df_bench[df_bench.apply(lambda row:
                                             row["name"] == name and
                                             row["nnodes"] == platform_config[platform]["nnodes"] and
                                             row["griddim"] == 8 and
                                             (not criteria_fn or criteria_fn(row)),
                                             axis=1)], "Total(s)", np.inf).apply(lambda x: 1 / x)
    return [total]


def extract_data(df_mbench, df_bench, config, platform, criteria_fn=None):
    mbench_data = extract_microbenchmark(df_mbench, config, platform, criteria_fn=criteria_fn)
    bench_data = extract_benchmark(df_bench, config, platform, criteria_fn=criteria_fn)
    return mbench_data + bench_data


def normalize_data(data, base):
    ret = []
    for d, b in zip(data, base):
        if d != 0 and b != 0:
            ret.append(d / b)
        else:
            ret.append(0)
    return ret
    # return [data[i] / base[i] for i in range(len(data))]


def apply_mask(l, mask):
    if mask:
        new_l = []
        for i in range(len(l)):
            if mask[i]:
                new_l.append(l[i])
        return new_l
    else:
        return l


def draw_diff(dfs, base, configs, filename, dirname="default", title=None, legend_loc="best", legend_fn=None, label_mask=None,
              criteria_fn=None):
    labels = ["Message Rate\n(8B)", "Message Rate\n(16KiB)", "1 / Latency\n(8B)", "1 / Latency\n(16KiB)", "Efficiency",
              "1 / OctoTiger\n(s)"]
    labels = apply_mask(labels, label_mask)
    dataset = []
    for platform, df in zip(platforms, dfs):
        df_mbench = df[0]
        df_bench = df[1]
        xs = []
        stds = []
        base_data = extract_data(df_mbench, df_bench, base, platform, criteria_fn=criteria_fn)
        if use_median:
            base_xs = [datum.median() for datum in base_data]
        else:
            base_xs = [datum.mean() for datum in base_data]
        for config in configs:
            current_data = extract_data(df_mbench, df_bench, config, platform, criteria_fn=criteria_fn)
            if use_median:
                current_xs = [datum.median() for datum in current_data]
            else:
                current_xs = [datum.mean() for datum in current_data]
            current_stds = [datum.std() for datum in current_data]
            for i, std in enumerate(current_stds):
                if pd.isna(std):
                    current_stds[i] = 0
            xs.append(apply_mask(normalize_data(current_xs, base_xs), label_mask))
            stds.append(apply_mask(normalize_data(current_stds, base_xs), label_mask))
        dataset.append({"xs": xs, "stds": stds})

    draw_bar(configs, dataset, labels, filename, dirname, title, legend_loc, legend_fn, with_error=with_error)


def batch(dfs):
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    def sort_key(x):
        ordering = {
            "lci": 0,
            "mpi": 1,
            "mpi_a": 2,
        }
        return ordering[x["label"]]

    draw_line([df[0] for df in dfs], "nthreads", "msg_rate(K/s)", "name",
              dirname="mpi_vs_lci", filename="flood-8",
              base="lci", smaller_is_better=False, with_error=True, sort_key=sort_key,
              xscale="log", yscale="log",
              x_label="Thread Number", y_label="Message Rate (K/s)",
              criteria_fn=lambda row: row["nbytes"] == 8 and
                                      row["nsteps"] == 1 and
                                      row["intensity"] == 0 and
                                      row["name"] in ["mpi", "mpi_a", "lci"] and
                                      row["pingpong_config_name"] == "flood")
    draw_line([df[0] for df in dfs], "nthreads", "msg_rate(K/s)", "name",
              dirname="mpi_vs_lci", filename="flood-16384",
              base="lci", smaller_is_better=False, with_error=True, sort_key=sort_key,
              x_label="Thread Number", y_label="Message Rate (K/s)",
              xscale="log", yscale="log",
              criteria_fn=lambda row: row["nbytes"] == 16384 and
                                      row["nsteps"] == 1 and
                                      row["intensity"] == 0 and
                                      row["name"] in ["mpi", "mpi_a", "lci"] and
                                      row["pingpong_config_name"] == "flood")
    draw_line([df[0] for df in dfs], "nchains", "latency(us)", "name",
              dirname="mpi_vs_lci", filename="nchains-8",
              base="lci", with_error=True, sort_key=sort_key,
              x_label="Chain Number", y_label="Latency (us)",
              xscale="log", yscale="log",
              criteria_fn=lambda row: row["nbytes"] == 8 and
                                      row["nsteps"] > 1 and
                                      row["name"] in ["mpi", "mpi_a", "lci"] and
                                      row["pingpong_config_name"] == "nchains")
    draw_line([df[0] for df in dfs], "nchains", "latency(us)", "name",
              dirname="mpi_vs_lci", filename="nchains-16384",
              base="lci", with_error=True, sort_key=sort_key,
              x_label="Chain Number", y_label="Latency (us)",
              xscale="log", yscale="log",
              criteria_fn=lambda row: row["nbytes"] == 16384 and
                                      row["nsteps"] > 1 and
                                      row["name"] in ["mpi", "mpi_a", "lci"] and
                                      row["pingpong_config_name"] == "nchains")

    draw_line([df[0] for df in dfs], "nbytes", "latency(us)", "name",
              dirname="mpi_vs_lci", filename="nbytes",
              base="lci", smaller_is_better=True, with_error=True, sort_key=sort_key,
              x_label="Message Size (B)", y_label="Latency (us)",
              xscale="log", yscale="log",
              criteria_fn=lambda row: row["nchains"] == 1024 and
                                      row["name"] in ["mpi", "lci", "mpi_a"] and
                                      row["pingpong_config_name"] == "nbytes",)

    # draw_line([df[0] for df in dfs], "task_comp_time", "efficiency", "name",
    #           dirname="mpi_vs_lci", filename="efficiency",
    #           base="lci", smaller_is_better=False, with_error=True, sort_key=sort_key,
    #           x_label="Task Granularity", y_label="Efficiency",
    #           xscale="log", yscale="log",
    #           criteria_fn=lambda row: row["nbytes"] == 16384 and
    #                                   row["nchains"] == 1024 and
    #                                   row["name"] in ["mpi", "lci", "mpi_a"] and
    #                                   row["pingpong_config_name"] == "comp",)

    draw_line([df[1] for df in dfs], "nnodes", "Total(s)", "name",
              dirname="mpi_vs_lci", filename="brief",
              base="lci", with_error=True, sort_key=sort_key,
              x_label="Node Count", y_label="Time to Solution (s)",
              xscale="log", yscale="log",
              criteria_fn=lambda row: row["name"] in ["lci", "mpi_a", "mpi"] and
                                      row["max_level"] == 5 and row["nnodes"] <= 256)

    draw_diff(dfs, "lci_2queue",
              ["lci_sendrecv",
               "lci_header_sync_single_nolock",
               "lci_header_sync_single", ],
              "incoming", dirname="config", title="Polling for unexpected incoming messages",
              label_mask=[1, 0, 1, 0, 0, 1],
              legend_loc="upper right", legend_fn=lambda x: {"lci_sendrecv": "sendrecv",
                                                             "lci_header_sync_single_nolock": "sync",
                                                             "lci_header_sync_single": "sync_lock"}[x],
              criteria_fn=lambda row: row["ndevices"] == 2 and row["ncomps"] == 2)
    draw_diff(dfs, "lci_sendcrecv",
              ["lci_followup_sync",
               "lci_followup_queue_mutex"],
              "followup", dirname="config", title="Managing a large number of pending operations",
              label_mask=[1, 1, 1, 1, 0, 1],
              legend_loc="upper left", legend_fn=lambda x: {"lci_sendcrecv": "sendcrecv",
                                                            "lci_followup_sync": "sync",
                                                            "lci_followup_sync_poll": "sync_poll",
                                                            "lci_followup_queue_mutex": "queue_mutex"}[x])

    # draw_diff(dfs, "lci",
    #           ["lci_followup_queue_mutex"],
    #             "queue_lock", title="Impact of a lock-based queue",
    #             label_mask=[1, 1, 1, 1, 1, 1],
    #             legend_loc="upper left", legend_fn=lambda x: {"lci_followup_queue_mutex": "queue_lock"}[x],)

    draw_diff(dfs, "lci_mt_d2_c1",
              ["lci_pin", "lci_pthread", "lci_pthread_worker"],
              "progress", dirname="config", title="Different ways of driving the progress engine",
              label_mask=[1, 1, 1, 1, 0, 1],
              legend_loc="upper left", legend_fn=lambda x: {"lci_pin": "pin",
                                                            "lci_pthread": "floating",
                                                            "lci_pthread_worker": "floating_mt"}[x])

    draw_line([df[0] for df in dfs], "ndevices", "msg_rate(K/s)", "ndevices_tag",
              dirname="config", filename="ndevices", with_error=True,
              xscale="log", yscale="log", sort_key=lambda x: {"base": 0, "try-lock": 1, "lock": 2}[x["label"]],
              x_label="Device Number", y_label="Message Rate (K/s)",
              criteria_fn=lambda row: row["nbytes"] == 8 and
                                      row["nchains"] == 1000000 and
                                      row["nsteps"] == 1 and
                                      row["pingpong_config_name"] == "flood" and
                                      row["ndevices_tag"] in ["base", "try-lock", "lock"])

    draw_line([df[1] for df in dfs], "ndevices", "Total(s)", "ndevices_tag",
              dirname="config", filename="ndevices-app", with_error=True,
              xscale="log", yscale="log", sort_key=lambda x: {"base": 0, "try-lock": 1, "lock": 2}[x["label"]],
              x_label="Device Number", y_label="Time to Solution (s)",
              criteria_fn=lambda row: row["ndevices_tag"] in ["base", "try-lock", "lock"] and
                                      row["max_level"] == 5)

    draw_diff(dfs,
              "lci_mt_d2_c1", ["lci_a", "mpi", "mpi_a"],
              "aggregation", dirname="config",
              label_mask=[1, 1, 1, 1, 0, 1],
              title="Aggregation")


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
    dfs = []
    for platform in platforms:
        df_mbench = preprocess_df(pd.read_csv(job_name_dict[platform]["mbench"]))
        df_bench = preprocess_df(pd.read_csv(job_name_dict[platform]["bench"]))
        dfs.append((df_mbench, df_bench))
    batch(dfs)
