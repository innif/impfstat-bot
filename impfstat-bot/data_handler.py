import util
from data_grabber import DataGrabber


class DataHandler:
    def __init__(self):
        self.data_grabber = DataGrabber()

        self.conf = util.read_json_file()
        self.doses_diff_avg: dict = {}

        self.newest_data_line: dict = {}
        self.doses_total: dict = {}
        self.doses_by_institution_total: dict = {}
        self.doses_by_institution_diff: dict = {}
        self.doses_by_institution_avg: dict = {}
        self.doses_diff: dict = {}

        self.data = self.data_grabber.data
        self.data_len = self.data_grabber.data_len
        self.dates = []

        self.update(force_update=True)

    def update(self, force_update=False) -> bool:
        new_data = self.data_grabber.update()
        if not force_update and not new_data:
            return False

        self.data = self.data_grabber.data
        self.data_len = self.data_grabber.data_len

        self._calc_newest_data_line()
        self._calc_doses_total()
        self._calc_doses_by_institution()

        self.dates = self.data["data"]["date"]

    def _calc_newest_data_line(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.newest_data_line = {}
        for key, val in zip(data.keys(), data.values()):
            self.newest_data_line[key] = val[data_len - 1]

    def _calc_doses_total(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.doses_total = {
            'biontech': [int(s) for s in data['dosen_biontech_kumulativ']],
            'astrazeneca': [int(s) for s in data['dosen_astrazeneca_kumulativ']],
            'moderna': [int(s) for s in data['dosen_moderna_kumulativ']],
            'johnson': [int(s) for s in data['dosen_johnson_kumulativ']],
        }
        for key in self.doses_total.keys():
            self.doses_diff[key] = [self.doses_total[key][0]]
            self.doses_diff[key] += [self.doses_total[key][i] - self.doses_total[key][i - 1] for i in
                                     range(1, data_len)]
            self.doses_diff_avg[key] = [sum(self.doses_diff[key][i - 7:i]) / 7 for i in range(data_len)]

    def _calc_doses_by_institution(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.doses_by_institution_total = {
            'Impfzentren': [int(s) for s in data['dosen_dim_kumulativ']],
            'Artztpraxen': [int(s) for s in data['dosen_kbv_kumulativ']],
        }
        for key in self.doses_by_institution_total.keys():
            self.doses_by_institution_diff[key] = [self.doses_by_institution_total[key][0]]
            self.doses_by_institution_diff[key] += [
                self.doses_by_institution_total[key][i] - self.doses_by_institution_total[key][i - 1]
                for i in range(1, data_len)]
            self.doses_by_institution_avg[key] = [sum(self.doses_by_institution_diff[key][i - 7:i]) / 7 for i in
                                                  range(data_len)]
