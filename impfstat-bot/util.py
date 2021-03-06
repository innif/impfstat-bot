import json
import logging
import os
from pathlib import Path

from telegram import Update


def get_resource_file_path(name: str, folder: str = "resources"):
    rel_path = "{}/{}".format(folder, name)
    base_path = Path(__file__).parent
    file_path = (base_path / rel_path).resolve()
    return str(file_path)


def get_resource_file(name: str, folder: str = "resources", mode: str = "r"):
    rel_path = "{}/{}".format(folder, name)
    base_path = Path(__file__).parent
    file_path = (base_path / rel_path).resolve()
    return open(file_path, mode, encoding="utf-8")


def log_message(update: Update):
    text = update.message.text.encode('ascii', 'ignore').decode('ascii')  # remove emoticons
    eff_msg = str(update.effective_message).encode('ascii', 'ignore').decode('ascii')
    logging.info("MSG: {} {} ### MESSAGE:{}".format(
        update.message.date, text,
        eff_msg))


def date(x: str) -> str:
    try:
        out = ""
        x_split = x.split(" ")
        d = x_split[0].split("-")
        if len(d) > 2:
            out += "{}.{}.{}".format(d[2], d[1], d[0])
        else:
            out += x_split[0]
        if len(x_split) > 1:
            out += " {}".format(x_split[1][:5])
        return out
    except Exception as e:
        logging.error(e)
        return x


def dec_points(x) -> str:
    return "{:,}".format(int(x)).replace(",", ".")


def to_percent(x) -> str:
    return "{:.1f}%".format(float(x) * 100).replace(".", ",")


def to_mio(x) -> str:
    return "{:.2f}".format(int(x) / 1000000).replace(".", ",")


def read_json_file(name: str = "config.json", folder: str = "resources") -> dict:
    try:
        conf_file = get_resource_file(name, folder=folder)
        conf: dict = json.load(conf_file)
        conf_file.close()
        return conf
    except Exception as e:
        logging.error(e)
        return {}


def write_json_file(content, name: str = "config.json", folder: str = "resources") -> None:
    try:
        conf_file = get_resource_file(name, folder=folder, mode="w")
        json.dump(content, conf_file)
        conf_file.close()
    except Exception as e:
        logging.error(e)
        return


def get_apikey() -> str:
    conf_file = get_resource_file("api-key.json")
    conf: dict = json.load(conf_file)
    api_key: str = conf["api-key"]
    if is_debug():
        api_key: str = conf["api-key-debug"]
    return api_key


def is_debug() -> bool:
    return os.path.isfile(get_resource_file_path("debug.flag"))


def delete_folder_content(folder: str, ending: str) -> None:
    base_path = Path(__file__).parent
    folder_path = (base_path / folder).resolve()
    for f in os.listdir(folder_path):
        if f.endswith(ending):
            file_path = (folder_path / f).resolve()
            os.remove(file_path)


def file_to_string(name, folder="resources"):
    f = get_resource_file(name, folder)
    lines = f.readlines()
    out = ""
    for line in lines:
        out += line
    f.close()
    return out
