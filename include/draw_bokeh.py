import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
from draw_simple import *
import numpy as np
import bokeh
import bokeh.plotting
import itertools

def create_plot(line_entries, x_key, y_key, tag_key, title,
                x_label=None, y_label=None,
                dirname = ".", filename = None):
    assert line_entries
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    p = bokeh.plotting.figure(title=title, x_axis_label=x_label, y_axis_label=y_label, width=1200, height=600, x_axis_type="log", y_axis_type="log")
    p.x_range.only_visible = True
    p.y_range.only_visible = True

    lines = []
    for entry, color in zip(line_entries, itertools.cycle(bokeh.palettes.Dark2_5)):
        line = p.line(x=entry["x"], y=entry["y"], legend_label=entry["label"], color=color, name=entry["label"])
        lines.append(line)

    legend = p.legend[0]
    legend.click_policy = "hide"
    p.add_layout(legend, "right")

    # create hover tool
    hover = bokeh.models.HoverTool(mode="vline", tooltips=[
        ("name", "$name"),
        (x_key, "$snap_x"),
        (y_key, '$snap_y'),
    ])
    hover.point_policy = 'snap_to_data'
    hover.line_policy = 'nearest'
    p.add_tools(hover)
    # Add button
    btn = bokeh.models.Button(label='Hide All')
    cb = bokeh.models.CustomJS(args=dict(fig=p, btn=btn)
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
    p = bokeh.layouts.column([p, btn])

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_path = os.path.join(dirname, "{}.html".format(filename))

    bokeh.io.output_file(filename=output_path, title=title)
    layout = bokeh.layouts.row(p)
    bokeh.plotting.save(layout)
    # bokeh.plotting.show(layout)

def plot_bokeh(df, x_key, y_key, tag_key, title,
               x_label=None, y_label=None,
               dirname=".", filename=None,
               label_fn=None, zero_x_is=0):

    df = df.sort_values(by=[tag_key, x_key])
    lines = parse_tag(df, x_key, y_key, tag_key)

    # update labels
    if label_fn is not None:
        for line in lines:
            line["label"] = label_fn(line["label"])
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    create_plot(lines, x_key, y_key, tag_key, title,
                x_label=x_label, y_label=y_label,
                dirname=dirname, filename=filename)