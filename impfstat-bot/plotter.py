import time

import matplotlib.pyplot as plt
import numpy as np

import util
from data_grabber import DataGrabber


def gen_stacked_plot(content, labels, n_samples, n_labels, title, path, x_label='Datum', y_label='Impfdosen', ):
    plt.ioff()
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
            "daily":        ("Täglich verabreichte Impfdosen",
                             self.data_grabber.doses_diff, "daily-plot.png", float(0)),
            "avg":          ("Täglich verabreichte Impfdosen im 7-Tages-Mittel",
                             self.data_grabber.doses_diff_avg, "avg-plot.png", float(0)),
            "sum":          ("Insgesamt verabreichte Impfdosen",
                             self.data_grabber.doses_total, "sum-plot.png", float(0)),
            "institution":  ("Täglich verabreichte Impfdosen nach Institution",
                             self.data_grabber.doses_by_institution_diff, "inst-daily-plot.png", float(0)),
            "inst-sum":     ("Summierte Impfdosen nach Institution",
                             self.data_grabber.doses_by_institution_total, "inst-total-plot.png", float(0)),
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
