import pandas as pd
import os,sys, json

from bokeh.io import output_file
from matplotlib import pyplot as plt
sys.path.append("../../include")
from draw_simple import *
import numpy as np
from bokeh.layouts import row, column
from bokeh.models import HoverTool, LegendItem, Legend, RangeSlider, Button
from bokeh.plotting import figure, show
from bokeh.palettes import Dark2_5 as palette, Bokeh
from bokeh.models import ColumnDataSource
from bokeh.models import CheckboxGroup, CustomJS
from bokeh.palettes import Viridis3
import itertools

job_name = "20240205-all"
input_path = "data/"
all_labels = ["name", "nbytes", "nchains", "intensity", "latency(us)", "msg_rate(K/s)", "bandwidth(MB/s)"]

def create_plot(line_entries, title, x_key, y_key):
    p = figure(title=title, x_axis_label=x_key, y_axis_label=y_key, width=1200, height=600, x_axis_type="log", y_axis_type="log")
    p.x_range.only_visible = True
    p.y_range.only_visible = True

    lines = []
    for entry, color in zip(line_entries, itertools.cycle(palette)):
        line = p.line(x=entry["x"], y=entry["y"], legend_label=entry["label"], color=color, name=entry["label"])
        lines.append(line)

    legend = p.legend[0]
    legend.click_policy = "hide"
    p.add_layout(legend, "right")

    # create hover tool
    hover = HoverTool(mode="vline", tooltips=[
        ("name", "$name"),
        (x_key, "$snap_x"),
        (y_key, '$snap_y'),
    ])
    hover.point_policy = 'snap_to_data'
    hover.line_policy = 'nearest'
    p.add_tools(hover)
    # Add button
    btn = Button(label='Hide All')
    cb = CustomJS(args=dict(fig=p, btn=btn)
                  ,code='''
                      if (btn.label=='Hide All'){
                          for (var i=0; i<fig.renderers.length; i++){
                                  fig.renderers[i].visible=false}
                          btn.label = 'Show All'
                          }
                      else {for (var i=0; i<fig.renderers.length; i++){
                              fig.renderers[i].visible=true}
                      btn.label = 'Hide All'}
                      ''')

    btn.js_on_click(cb)
    p = column([p, btn])

    return p

def plot(df, x_key, y_key, tag_key, title, filename = None, label_dict=None, with_error=True):
    if label_dict is None:
        label_dict = {}
    if title is None:
        title = filename

    df = df.sort_values(by=[tag_key, x_key])

    line_entries = parse_tag(df, x_key, y_key, tag_key)
    # update labels
    if label_dict is not None:
        for line in line_entries:
            print(line)
            label = line["label"]
            if label in label_dict:
                line["label"] = label_dict[line["label"]]

    return create_plot(line_entries, title, x_key, y_key)

def batch(df):
    # df["tag"] = np.where((df["parcelport"] == "lci") & (df["tag"] == "default"), "default-numa", df["tag"])
    # df["tag"] = np.where((df["parcelport"] == "lci") & (df["tag"] == "numalocal"), "default", df["tag"])
    figures = []
    # message rate
    df1_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["nsteps"] == 1,
                          # ("sendimm" in row["name"] or "mpi" in row["name"]),
                          # row["input_inject_rate(K/s)"] != 0,
                          axis=1)]
    df1 = df1_tmp.copy()
    p = plot(df1, "inject_rate(K/s)", "msg_rate(K/s)", "name", "message_rate-8", with_error=False)
    figures.append(p)

    df2_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nsteps"] == 1,
                          # ("sendimm" in row["name"] or "mpi" in row["name"]),
                          # row["input_inject_rate(K/s)"] != 0,
                          axis=1)]
    df2 = df2_tmp.copy()
    p = plot(df2, "inject_rate(K/s)", "msg_rate(K/s)", "name", "message_rate-16384", with_error=False)
    figures.append(p)

    # latency
    df3_tmp = df[df.apply(lambda row:
                          row["window"] == 1 and
                          row["nsteps"] > 1,
                          # ("sendimm" in row["name"] or "mpi" in row["name"]),
                          axis=1)]
    df3 = df3_tmp.copy()
    p = plot(df3, "nbytes", "latency(us)", "name", "latency", with_error=False)
    figures.append(p)

    # window - latency
    df3_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 8 and
                          row["nsteps"] > 1,
                          # ("sendimm" in row["name"] or "mpi" in row["name"]),
                          axis=1)]
    df3 = df3_tmp.copy()
    p = plot(df3, "window", "latency(us)", "name", "window-latency-8", with_error=False)
    figures.append(p)

    df3_tmp = df[df.apply(lambda row:
                          row["nbytes"] == 16384 and
                          row["nsteps"] > 1,
                          # ("sendimm" in row["name"] or "mpi" in row["name"]),
                          axis=1)]
    df3 = df3_tmp.copy()
    p = plot(df3, "window", "latency(us)", "name", "window-latency-16384", with_error=False)
    figures.append(p)

    # df3_tmp = df[df.apply(lambda row:
    #                       row["nbytes"] == 65536 and
    #                       row["nsteps"] > 1,
    #                       # ("sendimm" in row["name"] or "mpi" in row["name"]),
    #                       axis=1)]
    # df3 = df3_tmp.copy()
    # p = plot(df3, "window", "latency(us)", "name", "window-latency-65536", with_error=False)
    # figures.append(p)

    dirname = os.path.join("draw", job_name)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_name = os.path.join(dirname, "interactive.html")
    output_file(filename=output_name)

    layout = row(*figures)
    show(layout)

if __name__ == "__main__":
    df = pd.read_csv(os.path.join(input_path, job_name + ".csv"))
    # interactive(df)
    batch(df)
