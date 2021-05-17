import util
from data_grabber import DataGrabber


def delete_plots():
    util.delete_folder_content("plots", ".png")


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
        self.update_info = self.data_grabber.update_info
        self.dates = []

        self.proportions = {
            "Vollständig Geimpft": 0,
            "Teilweise Geimpft": 0,
            "ungeimpft": 0
        }

        self.update(force_update=True)

    def update(self, force_update=False) -> bool:
        new_data = self.data_grabber.update()
        if not force_update and not new_data:
            return False

        self.data = self.data_grabber.data
        self.data_len = self.data_grabber.data_len
        self.update_info = self.data_grabber.update_info

        self.__calc_newest_data_line()
        self.__calc_doses_total()
        self.__calc_doses_by_institution()

        self.dates = self.data["data"]["date"]

        full = float(self.newest_data_line["impf_quote_voll"])
        part = float(self.newest_data_line["impf_quote_erst"]) - full
        none = 1 - full - part

        self.proportions = {"Vollständig Geimpft": full, "Teilweise Geimpft": part, "ungeimpft": none}

        delete_plots()

    def __calc_newest_data_line(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.newest_data_line = {}
        for key, val in zip(data.keys(), data.values()):
            self.newest_data_line[key] = val[data_len - 1]

    def __calc_doses_total(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.doses_total = {
            'biontech': [int(s) for s in data['dosen_biontech_kumulativ']],
            'astrazeneca': [int(s) for s in data['dosen_astrazeneca_kumulativ']],
            'moderna': [int(s) for s in data['dosen_moderna_kumulativ']],
            'johnson': [int(s) for s in data['dosen_johnson_kumulativ']],
        }
        self.doses_diff, self.doses_diff_avg = self.__calc_div_avg(self.doses_total, data_len)

    def __calc_doses_by_institution(self):
        data = self.data["data"]
        data_len = self.data_len["data"]
        self.doses_by_institution_total = {
            'Impfzentren': [int(s) for s in data['dosen_dim_kumulativ']],
            'Artztpraxen': [int(s) for s in data['dosen_kbv_kumulativ']],
        }
        self.doses_by_institution_diff, self.doses_by_institution_avg = \
            self.__calc_div_avg(self.doses_by_institution_total, data_len)

    @staticmethod
    def __calc_div_avg(total: dict, data_len: int, avg_span: int = 7) -> (dict, dict):
        diff: dict = {}
        avg: dict = {}
        for key in total.keys():
            diff[key] = [total[key][0]]
            diff[key] += [total[key][i] - total[key][i - 1] for i in range(1, data_len)]
            avg[key] = [sum(diff[key][i - avg_span:i]) / avg_span for i in range(data_len)]
        return diff, avg
