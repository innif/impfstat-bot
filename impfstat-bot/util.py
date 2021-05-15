import json
import os
from pathlib import Path

from telegram import Update
from telegram.ext import CallbackContext


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


def log(update: Update, context: CallbackContext, tag="MSG"):
    f = None
    try:
        f = get_resource_file("log.txt", "logs", "a")
        f.write("{}\t".format(tag))
        if update is not None:
            f.write("{}\t{}\t{}\t###\tCHAT:{}\tMESSAGE:{}\n".format(
                update.message.date, update.message.chat.username, update.message.text, update.effective_chat,
                update.effective_message))
        else:
            f.write("\n")
    except:
        pass
    finally:
        if f is not None:
            f.close()


def date(x: str) -> str:
    d = x.split("-")
    return "{}.{}.{}".format(d[2], d[1], d[0])


def dec_points(x) -> str:
    return "{:,}".format(int(x)).replace(",", ".")


def to_percent(x) -> str:
    return "{:.1f}%".format(float(x) * 100).replace(".", ",")


def to_mio(x) -> str:
    return "{:.2f} Mio.".format(int(x) / 1000000).replace(".", ",")


def get_conf_file(name: str = "config.json") -> dict:
    conf_file = get_resource_file(name)
    conf: dict = json.load(conf_file)
    return conf


def get_apikey() -> str:
    conf_file = get_resource_file("api-key.json")
    conf: dict = json.load(conf_file)
    api_key: str = conf["api-key"]
    if os.path.isfile(get_resource_file_path("debug.flag")):
        api_key: str = conf["api-key-debug"]
    return api_key
