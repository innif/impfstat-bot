import csv
import os
import time

import requests

import util


class DataGrabber:
    def __init__(self):
        self.conf = util.get_conf_file()
        self.doses_diff_avg: dict = {}
        self.last_update = 0
        self.data_path = util.get_resource_file_path(self.conf["data_filename"], "data")
        self.url = self.conf["data-url"]
        self.data: dict = {}
        self.newest_data_line: dict = {}
        self.doses_total: dict = {}
        self.doses_by_institution_total: dict = {}
        self.doses_by_institution_diff: dict = {}
        self.doses_diff: dict = {}
        self.data_len = 0
        self.update()

    def update(self):
        if time.time() - self.last_update < (60 * 60):  # letztes Update weniger als eine Stunde her
            return
        self._get_vaccination_data()
        self._get_newest_data()
        self.last_update = time.time()
        self.doses_total = {
            'biontech': [int(s) for s in self.data['dosen_biontech_kumulativ']],
            'astrazeneca': [int(s) for s in self.data['dosen_astrazeneca_kumulativ']],
            'moderna': [int(s) for s in self.data['dosen_moderna_kumulativ']],
            'johnson': [int(s) for s in self.data['dosen_johnson_kumulativ']],
        }
        self.doses_by_institution_total = {
            'Impfzentren': [int(s) for s in self.data['dosen_dim_kumulativ']],
            'Artztpraxen': [int(s) for s in self.data['dosen_kbv_kumulativ']],
        }
        for key in self.doses_total.keys():
            self.doses_diff[key] = [self.doses_total[key][0]]
            self.doses_diff[key] += [self.doses_total[key][i] - self.doses_total[key][i - 1] for i in
                                     range(1, self.data_len)]
            self.doses_diff_avg[key] = [sum(self.doses_diff[key][i - 7:i]) / 7 for i in range(self.data_len)]

        for key in self.doses_by_institution_total.keys():
            self.doses_by_institution_diff[key] = [self.doses_by_institution_total[key][0]]
            self.doses_by_institution_diff[key] += [
                self.doses_by_institution_total[key][i] - self.doses_by_institution_total[key][i - 1]
                for i in range(1, self.data_len)]

    def _get_vaccination_data(self):
        if os.path.exists(self.data_path):
            file_age = time.time() - os.path.getmtime(self.data_path)
        else:
            file_age = float("inf")
        if file_age > (60 * 60):  # wenn Datei älter als eine Stunde ist...
            vacc_file = requests.get(self.url)
            with open(self.data_path, 'wb') as f:
                f.write(vacc_file.content)
        self.data = {}
        titles = []
        with open(self.data_path) as f:
            csv_reader = csv.reader(f, delimiter='\t')
            first_line = True
            for row in csv_reader:
                if first_line:
                    titles = row
                    for element in titles:
                        self.data[element] = []
                    first_line = False
                else:
                    for i, element in enumerate(row):
                        identifier = titles[i]
                        self.data[identifier].append(element)
        self.data_len = len(self.data["date"])

    def _get_newest_data(self):
        self.newest_data_line = {}
        for key, val in zip(self.data.keys(), self.data.values()):
            self.newest_data_line[key] = val[self.data_len - 1]
