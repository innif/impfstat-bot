import csv
import json
import logging
import time

import requests

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
        self.update()

    def update(self) -> bool:
        if time.time() - self.last_update < (30 * 60):  # letztes Update weniger als eine Stunde her
            return False
        if self._get_vaccination_data():
            self.last_update = time.time()
            return True
        return False

    def _get_vaccination_data(self) -> bool:
        update_info_file = requests.get(self.conf["data-update-info-url"])
        update_info = json.loads(update_info_file.content.decode("utf-8"))
        updated = False

        if update_info.get("vaccinationsLastUpdated") != self.update_info.get("vaccinationsLastUpdated"):
            self.update_info["vaccinationsLastUpdated"] = update_info["vaccinationsLastUpdated"]
            self._get_data("data")
            self._get_data("by_state")
            updated = True

        if update_info.get("deliveryLastUpdated") != self.update_info.get("deliveryLastUpdated"):
            self.update_info["deliveryLastUpdated"] = update_info["deliveryLastUpdated"]
            self._get_data("deliveries")
            updated = True

        return updated

    def _get_data(self, data_type: str):
        if data_type not in self.sources.keys():
            logging.warning("{} is not in sources.keys()")
            return
        url = self.sources[data_type]["url"]
        path = self.sources[data_type]["path"]
        path = util.get_resource_file_path(path, "data")
        file = requests.get(url)
        with open(path, 'wb') as f:
            f.write(file.content)

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
