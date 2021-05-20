import csv
import json
import logging
import time

import urllib.request

import util


class DataGrabber:
    def __init__(self):
        self.conf: dict = util.read_json_file()
        self.sources: dict = self.conf["source"]
        self.last_update: int = 0
        self.data: dict = {}
        self.data_len = {}
        for k in self.sources.keys():
            self.data[k] = {}
            self.data_len[k] = 0
        self.update_info = {
            "vaccinationsLastUpdated": "never",
            "deliveryLastUpdated": "never"
        }
        self.update(force_update=True)

    def update(self, force_update=False) -> bool:
        if not force_update and time.time() - self.last_update < (self.conf["update-frequency"] * 60):
            return False  # letztes Update weniger als 10min her
        if self.__get_vaccination_data():
            self.last_update = time.time()
            return True
        return False

    def __get_vaccination_data(self) -> bool:
        path = util.get_resource_file_path(self.conf["data-update-info-filename"], "data")
        try:
            path, http_msg = urllib.request.urlretrieve(self.conf["data-update-info-url"], path)
        except Exception as e:
            logging.warning(e)
            return False

        update_info: dict = json.load(open(path))
        updated: bool = False
        try:
            if update_info.get("vaccinationsLastUpdated") != self.update_info.get("vaccinationsLastUpdated"):
                self.update_info["vaccinationsLastUpdated"] = update_info["vaccinationsLastUpdated"]
                self.__get_data("data")
                self.__get_data("by_state")
                updated = True

            if update_info.get("deliveryLastUpdated") != self.update_info.get("deliveryLastUpdated"):
                self.update_info["deliveryLastUpdated"] = update_info["deliveryLastUpdated"]
                self.__get_data("deliveries")
                updated = True
        except Exception as e:
            logging.warning(e)
            return False

        return updated

    def __get_data(self, data_type: str):
        if data_type not in self.sources.keys():
            logging.warning("{} is not in sources.keys()")
            return
        path = self.sources[data_type]["path"]
        path = util.get_resource_file_path(path, "data")
        url = self.sources[data_type]["url"]
        try:
            path, http_msg = urllib.request.urlretrieve(url, path)
        except Exception as e:
            logging.warning(e)
            return

        titles = []
        with open(path) as f:
            csv_reader = csv.reader(f, delimiter='\t')
            first_line = True
            for row in csv_reader:
                if first_line:
                    titles = row
                    for element in titles:
                        self.data[data_type][element] = []
                    first_line = False
                else:
                    for i, element in enumerate(row):
                        identifier = titles[i]
                        self.data[data_type][identifier].append(element)
        data: dict = self.data[data_type]
        for k in data.keys():
            self.data_len[data_type] = len(data[k])
            break
