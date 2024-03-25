import glob
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from tabulate import tabulate

name="octotiger"
input_file = "run/octotiger_analysis.*.out"
# input_file2 = "run-{}/slurm_output.analysis.n32-{}.*.out".format(name, name)
if __name__ == "__main__":
    # filenames = glob.glob(input_file2)
    # assert len(filenames) == 1
    # with open(filenames[0], "r") as infile:
    #     lines = infile.readlines()
    # pattern = "Time scope (?P<scope>\d+) (?P<action>\S+) at (?P<time>\S+) s"
    # time_scope = {}
    # for line in lines:
    #     m = re.match(pattern, line)
    #     if not m:
    #         continue
    #     scope = m.group("scope")
    #     action = m.group("action")
    #     time = float(m.group("time"))
    #     if scope not in time_scope:
    #         time_scope[scope] = []
    #     if action == "start":
    #         time_scope[scope].append([time])
    #     else:
    #         time_scope[scope][-1].append
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    filenames = glob.glob(input_file)
    lines = list()
    for filename in filenames:
        with open(filename, "r") as infile:
            lines += infile.readlines()

    # 0:medusa02.rostam.cct.lsu.edu:698663:0:/home/jiakun/workspace/hpx/libs/core/lci_base/src/lci_environment.cpp:log:244<hpx_lci:profile:send> 0:907274.183138:send_connection(0x337d8190) start:1:1162:0:0:[]
    pattern = ".*<hpx_lci:profile:send> (?P<rank>\d+):(?P<start_time>\S+):send_connection\((?P<p>\S+)\) start:(?P<dst_rank>\d+):(?P<nzc_size>\d+):(?P<tchunk_size>\d+):(?P<zc_num>\d+):\[(?P<chunks>\S+)?\]"
    src_rank_list = []
    dst_rank_list = []
    start_time_list = []
    nzc_size_list = []
    tchunk_size_list = []
    zc_num_list = []
    chunks_list = []
    total_size_list = []
    count = 0
    percent = 0
    base_time_map = {}
    for line in lines:
        if float(len(lines)) * percent / 10 <= count:
            percent += 1
            print("{}/{}".format(count, len(lines)))
        count += 1
        m = re.match(pattern, line)
        if not m:
            continue
        total_size = 0
        src_rank = int(m.group("rank"))
        start_time = float(m.group("start_time"))
        if src_rank not in base_time_map:
            base_time_map[src_rank] = start_time
            start_time = 0
        else:
            start_time -= base_time_map[src_rank]
        src_rank_list.append(src_rank)
        dst_rank_list.append(int(m.group("dst_rank")))
        start_time_list.append(start_time)
        nzc_size_list.append(int(m.group("nzc_size")))
        total_size += int(m.group("nzc_size"))
        if int(m.group("zc_num")) > 0:
            tchunk_size_list.append(int(m.group("tchunk_size")))
            total_size += int(m.group("tchunk_size"))
        zc_num_list.append(int(m.group("zc_num")))
        if m.group("chunks"):
            for chunk in m.group("chunks").split(","):
                chunks_list.append(int(chunk))
                total_size += int(chunk)
        total_size_list.append(total_size)

    assert len(start_time_list) > 0

    def draw_heatmap(ax, name, xs, ys, data):
        assert len(xs) == len(ys) == len(data)
        heat = np.zeros((np.max(xs) + 1, np.max(ys) + 1))
        print(heat)
        for i in range(len(data)):
            heat[xs[i], ys[i]] += data[i]
        print(heat)
        ax.imshow(heat)
        for i in range(heat.shape[0]):
            for j in range(heat.shape[1]):
                text = ax.text(j, i, int(heat[i, j]),
                               ha="center", va="center", color="w")
        ax.set_title(name)

    fig, ax = plt.subplots()
    draw_heatmap(ax, "nmsgs", src_rank_list, dst_rank_list, np.ones(len(src_rank_list)))
    fig.tight_layout()
    plt.savefig("draw/{}-nmsgs.png".format(name))

    fig, ax = plt.subplots()
    draw_heatmap(ax, "nbytes (MB)", src_rank_list, dst_rank_list, np.array(total_size_list) / 1e6)
    fig.tight_layout()
    plt.savefig("draw/{}-nbytes.png".format(name))

    def stat_and_draw(ax, name, data, bins=200, x_label=None, y_label=None):
        if len(data) == 0:
            return
        data_np = np.array(data)
        ax.hist(data, bins=bins, weights=np.ones(len(data)) / len(data))
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_title(name)
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        return [name, len(data_np), data_np.mean(), data_np.std(), data_np.min(), data_np.max()]

    def stat_and_draw_time(ax, name, data):
        if len(data) == 0:
            return
        data_np = np.array(data)
        base_time = np.min(data_np)
        data_np -= base_time
        duration = np.max(data_np)
        print(duration)
        n, bins, patches = ax.hist(data_np, bins=int(duration / 0.1))
        # for i, scope in enumerate(time_scope):
        #     for j, (start, end) in enumerate(time_scope[scope]):
        #         start = start - base_time
        #         end = end - base_time
        #         y = - ((i + 1) + j * 0.1) * max(n) / 10
        #         ax.plot([start, end], [y, y], color="C"+str(i))
        ax.set_title(name)
        return [name, len(data_np), data_np.mean(), data_np.std(), np.min(data_np), np.max(data_np)]


    def draw_trend(ax, name, time, data, x_label=None, y_label=None, y2_label=None):
        if len(data) == 0:
            return
        time_np = np.array(time)
        data_np = np.array(data)
        base_time = np.min(time_np)
        time_np -= base_time
        duration = np.max(time_np)
        print(duration)
        n, bins, patches = ax.hist(time_np, bins=int(duration / 0.1), label=y_label)
        # for i, scope in enumerate(time_scope):
        #     for j, (start, end) in enumerate(time_scope[scope]):
        #         start = start - base_time
        #         end = end - base_time
        #         y = - ((i + 1) + j * 0.1) * max(n) / 10
        #         ax.plot([start, end], [y, y], color="C"+str(i), linewidth=5)
        trend_x = []
        trend_y = []
        start = 0
        for i in range(len(bins) - 1):
            print(bins[i])
            print(n[i])
            num = int(n[i])
            trend_x.append((bins[i] + bins[i+1]) / 2)
            trend_y.append(data_np[start:start + num - 1].sum())
            start += num
        print(trend_x)
        print(trend_y)
        ax2 = ax.twinx()
        ax2.plot(trend_x, trend_y, color="C1", label=y2_label)
        ax.set_title(name)
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='best', ncol=1, fancybox=True)
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        if y2_label is not None:
            ax2.set_ylabel(y2_label)

    fig, ax = plt.subplots()
    draw_trend(ax, "Messages Over Time", start_time_list, total_size_list,
               x_label="Time (s)", y_label="Number", y2_label="Bytes")
    fig.tight_layout()
    plt.savefig("draw/{}-size_trend.png".format(name))

    fig, ax = plt.subplots()
    stat_and_draw(ax, "Message Size Distribution", nzc_size_list + total_size_list,
                  x_label="Message Size (B)", y_label="Percentage", bins=100)
    fig.tight_layout()
    plt.savefig("draw/{}-size_dist.png".format(name))

    # fig, axs = plt.subplots(2, 3, figsize=(20, 10))
    # data = []
    # # data.append(stat_and_draw_time(axs[0][0], "start time", start_time_list, time_scope))
    # draw_trend(axs[0][0], "message size trend", start_time_list, total_size_list)
    # data.append(stat_and_draw(axs[0][1], "nzc chunk size", nzc_size_list))
    # data.append(stat_and_draw(axs[0][2], "tchunk size", tchunk_size_list))
    # data.append(stat_and_draw(axs[1][0], "zc chunk number", zc_num_list))
    # data.append(stat_and_draw(axs[1][1], "zc chunk size", chunks_list))
    # axs[1][2].set_axis_off()

    # def format_text(headers, data):
    #     format_row = "{:>12}" * (len(headers) + 1) + "\n"
    #     text = format_row.format("", *headers)
    #     for entry in data:
    #         text += format_row.format("", *entry)
    #     return text
    # text = format_text(["Name", "Count", "Mean", "STD", "Min", "Max"], data)

    # text = tabulate(data, headers=["Name", "Count", "Mean", "STD", "Min", "Max"])
    # print(text)
    # axs[1][2].text(0, 0, text, fontsize = 10)
    # plt.tight_layout()
    # plt.savefig("draw/{}.png".format(name))


