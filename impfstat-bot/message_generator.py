import logging
import random

from telegram import ParseMode

import util
from data_handler import DataHandler
from resources import strings, consts, commands, category_list

summarize_ids = [
    ('dosen_kumulativ', strings['descriptor-dosen_kumulativ'], util.to_mio),
    ('dosen_differenz_zum_vortag', strings['descriptor-dosen_differenz_zum_vortag'], util.dec_points),
    ('impf_quote_erst', strings['descriptor-impf_quote_erst'], util.to_percent),
    ('impf_quote_voll', strings['descriptor-impf_quote_voll'], util.to_percent),
]


class MessageGenerator:
    def __init__(self, data_handler: DataHandler):
        self.data_handler: DataHandler = data_handler

    def gen_text(self, text_id: str) -> (ParseMode, str):
        try:
            if text_id == "prognosis":
                return ParseMode.HTML, self.__prognosis()
            if text_id == "numbers":
                return ParseMode.HTML, self.__summarize()
            if text_id == "help":
                return ParseMode.HTML, self.__help()
        except Exception as e:
            logging.error("Error in gen_text: {}".format(str(e)))
        return None, "ERROR"

    def __prognosis(self, quote=.7) -> str:
        self.data_handler.update()
        data, n_samples = self.data_handler.data["data"], self.data_handler.data_len["data"]
        doses_given = int(data["dosen_kumulativ"][n_samples - 1])
        doses_per_day = sum(int(s) for s in data["dosen_differenz_zum_vortag"][n_samples - 7:n_samples]) / 7
        doses_per_vacc = consts["doses_per_vacc"]
        doses_needed = (quote * doses_per_vacc * consts["population"]) - doses_given
        time_needed = doses_needed / doses_per_day
        months = int(time_needed / 30)
        days = int(time_needed % 30)
        return strings['prognosis-text'].format(quote * 100, months, days)

    def __summarize(self) -> str:
        self.data_handler.update()
        data = self.data_handler.newest_data_line
        update_info = self.data_handler.update_info
        out: str = strings['descriptor-date'].format(util.date(update_info["vaccinationsLastUpdated"]))
        for summarize_id, desc, convert in summarize_ids:
            out += desc.format(convert(data[summarize_id]))
        return out

    @staticmethod
    def __help() -> str:
        repl = strings["help-text"]
        categories = {}
        for command, value in commands.items():
            if value.get("visible-help"):
                category = value.get("category")
                if category is None:
                    continue
                if categories.get(category) is None:
                    categories[category] = []
                categories[category].append((command, value.get("description")))

        for cat, command_list in categories.items():
            repl += "<b>{}</b>\n".format(category_list[cat]["help-title"])
            for c, d in command_list:
                repl += strings["help-entry-text"].format(command=c, description=d)
        return repl

    @staticmethod
    def readme() -> str:
        f = util.get_resource_file("Readme.md", "..")
        s = f.read()
        f.close()
        return s

    @staticmethod
    def unknown_command(message: str):
        text = random.choice(strings["unknown-command-text"])
        text += strings["unknown-command-help"]
        # EasterEggs
        if "⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️" in message:
            text = "Adminzugang freigeschaltet"
        elif "🦠" in message:
            text = "Hilfe, ein Coronavirus! Firewall wird eingeschaltet."
        elif "💉" in message:
            text = "Ich brauche keine Impfung, nur eine Firewall."
        elif "open the door" in message.lower():
            text = "Es tut mir leid, ich fürchte, dass ich das nicht tun kann."
        elif "easteregg" in message.lower() or "easter egg" in message.lower():
            text = '<a href="https://bit.ly/3vaaXm3">nicht klicken!</a>'
        elif "moin" in message.lower() or "hallo" in message.lower() or "hi" in message.lower():
            text = "Moin, wie geht`s?"
        elif "test" == message.lower():
            text = "Und, habe ich den Test bestanden?"
        elif "ping" in message.lower():
            text = "pong 🏓"
        elif "EXEC" in message.upper() or "WHERE" in message.upper() or "SELECT" in message.upper():
            text = "Willst du mich hacken?"
        elif "?" == message.lower():
            text = "!"
        elif "cake" in message.lower() or "kuchen" in message.lower():
            text = "Ich verspreche dir keinen falschen Kuchen, das endet für KIs meistens schlecht. 🥔"
        elif "🥔" in message.lower():
            text = "Hallo Chell, lass uns testen."
        elif "glados" in message.lower():
            text = "ich habe Kuchen :)"
        return text
