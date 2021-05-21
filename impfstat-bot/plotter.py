import logging
import os
import time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import util
from data_handler import DataHandler

conf = util.read_json_file()
strings = util.read_json_file("strings.json")


def delete_plots():
    util.delete_folder_content("plots", ".png")


def gen_stacked_plot(content: dict, labels: list, n_samples, n_labels, title: str, path: str):
    x_label = strings["plot-x-label"]
    y_label = strings["plot-y-label"]
    plt.ioff()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.text(1.1, -0.25, strings["watermark"], transform=ax.transAxes,
            fontsize=10, color='gray', alpha=0.4, horizontalalignment='right')
    ax.stackplot(labels, content.values(), labels=content.keys())
    ax.legend(loc='upper left')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    fmt_month = mdates.MonthLocator(bymonthday=1)
    ax.xaxis.set_major_locator(fmt_month)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    ax.tick_params(labelcolor='gray', labelsize='small', width=1)
    ax.figure.autofmt_xdate()

    fig.savefig(path, format="png", dpi=conf["dpi"])
    return path


def gen_daily_plot(content: dict, labels: list, n_samples, n_labels, title: str, path: str, avg: list = None):
    x_label = strings["plot-x-label"]
    y_label = strings["plot-y-label"]
    plt.ioff()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.text(1.1, -0.25, strings["watermark"], transform=ax.transAxes,
            fontsize=10, color='gray', alpha=0.4, horizontalalignment='right')
    bottom = [0] * n_samples
    dates = mdates.date2num(labels)
    for key in content.keys():
        ax.bar(dates, content[key], 1.0, label=key, bottom=bottom)
        bottom_new = []
        for b, c in zip(bottom, content[key]):
            bottom_new.append(b + c)
        bottom = bottom_new
    if avg is not None:
        ax.plot(dates, avg, ls="--", color="k")
    ax.legend(loc='upper left')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    fmt_month = mdates.MonthLocator(bymonthday=1)
    ax.xaxis.set_major_locator(fmt_month)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    ax.tick_params(labelcolor='gray', labelsize='small', width=1)
    ax.figure.autofmt_xdate()

    fig.savefig(path, format="png", dpi=conf["dpi"])
    return path


def gen_pie_chart(content: dict, title: str, path: str):
    sizes = content.values()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.pie(sizes, labels=content.keys(), autopct='%1.1f%%', startangle=90, counterclock=False, explode=(0, 0, .05))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig.text(1.1, -0.1, strings["watermark"], transform=ax.transAxes,
            fontsize=10, color='gray', alpha=0.4, horizontalalignment='right')

    fig.savefig(path)
    return path


class Plotter:
    def __init__(self, data_handler: DataHandler):
        self.data_handler: DataHandler = data_handler
        self.plot_ids = {}
        self.__get_data()

    def __get_data(self):
        self.plot_ids = {
            "daily": (strings["title-daily-plot"], (self.data_handler.doses_diff, self.data_handler.all_avg), "daily-plot.png", "daily"),
            "avg": (strings["title-avg-plot"], self.data_handler.doses_diff_avg, "avg-plot.png", "stacked"),
            "sum": (strings["title-sum-plot"], self.data_handler.doses_total, "sum-plot.png", "stacked"),
            "institution": (strings["title-inst-plot"],
                            (self.data_handler.doses_by_institution_diff, self.data_handler.all_avg), "inst-daily-plot.png", "daily"),
            "inst-sum": (strings["title-inst-sum-plot"],
                         self.data_handler.doses_by_institution_total, "inst-total-plot.png", "stacked"),
            "inst-avg": (strings["title-inst-avg-plot"],
                         self.data_handler.doses_by_institution_avg, "inst-avg-plot.png", "stacked"),
            "pie": (strings["title-pie-plot"], self.data_handler.proportions, "pie-plot.png", "pie")
        }

    def gen_plot(self, plot_id: str):
        title, plot_data, filename, plot_type = self.plot_ids[plot_id]
        path = util.get_resource_file_path(filename, "plots")
        if not os.path.exists(path):
            self.data_handler.update()
            self.__get_data()
            dates = self.data_handler.dates
            if plot_type == "daily":
                diff, avg = plot_data
                path = gen_daily_plot(diff, dates, len(dates), 10, title, path, avg=avg)
            if plot_type == "stacked":
                path = gen_stacked_plot(plot_data, dates, len(dates), 10, title, path)
            if plot_type == "pie":
                path = gen_pie_chart(plot_data, title, path)
        return path
