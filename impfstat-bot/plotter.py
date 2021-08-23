import logging
import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import util
from data_handler import DataHandler
from resources import strings, conf


def gen_stacked_plot(content: dict, labels: list, title: str, path: str,
                     scale_factor: float = 1., scale_label="", deliveries: list = None):
    x_label = strings["plot-x-label"]
    y_label = strings["plot-y-label"] + scale_label
    dates = np.array(labels, dtype='datetime64[us]')
    plt.ioff()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.text(1.1, -0.25, strings["watermark"], transform=ax.transAxes,
            fontsize=10, color='gray', alpha=0.4, horizontalalignment='right')
    scaled_content: dict = {}
    for key in content.keys():
        scaled_content[key] = [c/scale_factor for c in content[key]]
    if deliveries is not None:
        ax.bar(dates, [d/scale_factor for d in deliveries], 0.5, label="Lieferungen", color="gray")
    ax.stackplot(dates, scaled_content.values(), labels=scaled_content.keys(), zorder=2)
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


def gen_daily_plot(content: dict, labels: list, n_samples, title: str, path: str, avg: list = None,
                   scale_factor: float = 1., scale_label=""):
    x_label = strings["plot-x-label"]
    y_label = strings["plot-y-label"]+scale_label
    plt.ioff()
    plt.style.use(conf["plt-style"])
    fig, ax = plt.subplots()
    ax.text(1.1, -0.25, strings["watermark"], transform=ax.transAxes,
            fontsize=10, color='gray', alpha=0.4, horizontalalignment='right')
    bottom = [0] * n_samples
    dates = np.array(labels, dtype='datetime64[us]')
    for key in content.keys():
        content_scaled = [c / scale_factor for c in content[key]]
        ax.bar(dates, content_scaled, 1.0, label=key, bottom=bottom)
        bottom_new = []
        for b, c in zip(bottom, content_scaled):
            bottom_new.append(b + c)
        bottom = bottom_new
    if avg is not None:
        avg_scaled = [a / scale_factor for a in avg]
        ax.plot(dates, avg_scaled, label=strings["avg-label"], ls="--", color="k")
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
    fig.text(1.1, -0.1, strings["watermark"], transform=ax.transAxes, fontsize=10, color='gray', alpha=0.4,
             horizontalalignment='right')

    fig.savefig(path, format="png", dpi=conf["dpi"])
    return path


class Plotter:
    def __init__(self, data_handler: DataHandler):
        self.data_handler: DataHandler = data_handler
        self.plot_ids = {}
        self.__get_data()

    def __get_data(self):
        self.plot_ids = {
            "daily": (strings["title-daily-plot"], (self.data_handler.doses_diff, self.data_handler.all_avg),
                      "daily-plot.png", "daily"),
            "avg": (strings["title-avg-plot"], (self.data_handler.doses_diff_avg, None),
                    "avg-plot.png", "stacked"),
            "sum": (strings["title-sum-plot"], (self.data_handler.doses_total, self.data_handler.deliveries),
                    "sum-plot.png", "stacked"),
            "institution": (strings["title-inst-plot"],
                            (self.data_handler.doses_by_institution_diff, self.data_handler.all_avg),
                            "inst-daily-plot.png", "daily"),
            "inst-sum": (strings["title-inst-sum-plot"],
                         (self.data_handler.doses_by_institution_total, self.data_handler.deliveries),
                         "inst-total-plot.png", "stacked"),
            "inst-avg": (strings["title-inst-avg-plot"],
                         (self.data_handler.doses_by_institution_avg, None), "inst-avg-plot.png", "stacked"),
            "pie": (strings["title-pie-plot"], self.data_handler.proportions, "pie-plot.png", "pie")
        }

    def get_plot(self, plot_id: str):
        try:
            title, plot_data, filename, plot_type = self.plot_ids[plot_id]
            path = util.get_resource_file_path(filename, "plots")
            if not os.path.exists(path):
                logging.info("generating plot {}".format(plot_id))
                self.data_handler.update()
                self.__get_data()
                dates = self.data_handler.dates
                if plot_type == "daily":
                    diff, avg = plot_data
                    path = gen_daily_plot(diff, dates, len(dates), title, path, avg=avg, scale_factor=1e6,
                                          scale_label=" (in Mio)")
                if plot_type == "stacked":
                    data, deliveries = plot_data
                    path = gen_stacked_plot(data, dates, title, path, deliveries=deliveries, scale_factor=1e6,
                                            scale_label=" (in Mio)")
                if plot_type == "pie":
                    path = gen_pie_chart(plot_data, title, path)
            return path
        except Exception as e:
            logging.error(e)
            return None

    @staticmethod
    def delete_plots():
        util.delete_folder_content("plots", ".png")

    def render_all(self):
        for plot_id in self.plot_ids.keys():
            self.get_plot(plot_id)

