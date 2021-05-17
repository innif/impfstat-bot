import logging
import os
import time

import matplotlib.pyplot as plt
import numpy as np

import util
from data_handler import DataHandler

conf = util.read_json_file()
strings = util.read_json_file("strings.json")


def delete_plots():
    util.delete_folder_content("plots", ".png")


def gen_stacked_plot(content: dict, labels: list, n_samples, n_labels, title: str, path: str, x_label=None,
                     y_label=None):
    if x_label is None:
        x_label = strings["plot-x-label"]
    if y_label is None:
        y_label = strings["plot-y-label"]
    plt.ioff()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.stackplot(labels, content.values(), labels=content.keys())
    ax.legend(loc='upper left')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.figure.autofmt_xdate()
    ax.set_xticks(np.arange(0, n_samples, n_samples / n_labels))
    fig.savefig(path)
    return path


def gen_pie_chart(content: dict, title: str, path: str):
    sizes = content.values()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.pie(sizes, labels=content.keys(), autopct='%1.1f%%', startangle=90, counterclock=False, explode=(0, 0, .05))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    fig.savefig(path)
    return path


class Plotter:
    def __init__(self, data_handler: DataHandler):
        self.data_handler: DataHandler = data_handler
        self.stacked_types = {}
        self.pie_types = {}
        self.__get_data()

    def __get_data(self):
        self.stacked_types = {
            "daily": (strings["title-daily-plot"], self.data_handler.doses_diff, "daily-plot.png"),
            "avg": (strings["title-avg-plot"], self.data_handler.doses_diff_avg, "avg-plot.png"),
            "sum": (strings["title-sum-plot"], self.data_handler.doses_total, "sum-plot.png"),
            "institution": (strings["title-inst-plot"],
                            self.data_handler.doses_by_institution_diff, "inst-daily-plot.png"),
            "inst-sum": (strings["title-inst-sum-plot"],
                         self.data_handler.doses_by_institution_total, "inst-total-plot.png"),
            "inst-avg": (strings["title-inst-avg-plot"],
                         self.data_handler.doses_by_institution_avg, "inst-avg-plot.png"),
        }
        self.pie_types = {
            "pie": (strings["title-pie-plot"], self.data_handler.proportions, "pie-plot.png")
        }

    def gen_plot(self, plot_type: str):
        if plot_type in self.pie_types.keys():
            title, plot_data, filename = self.pie_types[plot_type]
        elif plot_type in self.stacked_types.keys():
            title, plot_data, filename = self.stacked_types[plot_type]
        else:
            logging.error("unknown plot_type: {}".format(plot_type))
            return None
        path = util.get_resource_file_path(filename, "plots")
        if not os.path.exists(path):
            self.data_handler.update()
            self.__get_data()
            if plot_type in self.pie_types.keys():
                gen_pie_chart(plot_data, title, path)
            elif plot_type in self.stacked_types.keys():
                dates = self.data_handler.dates
                gen_stacked_plot(plot_data, dates, len(dates), 10, title, path)
                self.stacked_types[plot_type] = title, plot_data, filename
        return path
