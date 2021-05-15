import time

import matplotlib.pyplot as plt
import numpy as np

import util
from data_grabber import DataGrabber

conf = util.read_json_file()
strings = util.read_json_file("strings.json")


def gen_stacked_plot(content, labels, n_samples, n_labels, title, path, x_label=None, y_label=None):
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


class Plotter:
    def __init__(self, data_grabber: DataGrabber):
        self.data_grabber: DataGrabber = data_grabber
        self.types = {
            "daily":    (strings["title-daily-plot"], self.data_grabber.doses_diff, "daily-plot.png", float(0)),
            "avg":      (strings["title-avg-plot"], self.data_grabber.doses_diff_avg, "avg-plot.png", float(0)),
            "sum":      (strings["title-sum-plot"], self.data_grabber.doses_total, "sum-plot.png", float(0)),
            "institution":  (strings["title-inst-plot"],
                             self.data_grabber.doses_by_institution_diff, "inst-daily-plot.png", float(0)),
            "inst-sum":     (strings["title-inst-sum-plot"],
                             self.data_grabber.doses_by_institution_total, "inst-total-plot.png", float(0)),
            "inst-avg":     (strings["title-inst-avg-plot"],
                             self.data_grabber.doses_by_institution_avg, "inst-avg-plot.png", float(0)),
        }

    def gen_plot(self, plot_type: str):
        title, plot_data, filename, latest_update = self.types[plot_type]
        path = util.get_resource_file_path(filename, "plots")
        if time.time() > latest_update * (10*60):
            self.data_grabber.update()
            data = self.data_grabber.data
            gen_stacked_plot(plot_data, data['date'], self.data_grabber.data_len, 10, title, path)
            self.types[plot_type] = title, plot_data, filename, time.time()
        return path
