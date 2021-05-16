import util
from data_handler import DataHandler

consts = util.read_json_file("constants.json")
strings = util.read_json_file("strings.json")
conf = util.read_json_file()

summarize_ids = [
    ('dosen_kumulativ', strings['descriptor-dosen_kumulativ'], util.to_mio),
    ('dosen_differenz_zum_vortag', strings['descriptor-dosen_differenz_zum_vortag'], util.dec_points),
    ('impf_quote_erst', strings['descriptor-impf_quote_erst'], util.to_percent),
    ('impf_quote_voll', strings['descriptor-impf_quote_voll'], util.to_percent),
]


class MessageGenerator:
    def __init__(self, data_handler: DataHandler):
        self.data_handler: DataHandler = data_handler

    def prognosis(self, quote=.7) -> str:
        self.data_handler.update()
        data, n_samples = self.data_handler.data["data"], self.data_handler.data_len["data"]
        doses_given = int(data["dosen_kumulativ"][n_samples - 1])
        doses_per_day = sum(int(s) for s in data["dosen_differenz_zum_vortag"][n_samples - 7:n_samples]) / 7
        doses_per_vacc = consts["doses_per_vacc"]
        doses_needed = (quote * doses_per_vacc * consts["population"]) - doses_given
        time_needed = doses_needed / doses_per_day
        months = int(time_needed / 30)
        days = int(time_needed % 30)
        return strings['prognosis-text'].format(
            quote * 100, months, days)

    def summarize(self) -> str:
        self.data_handler.update()
        data = self.data_handler.newest_data_line
        update_info = self.data_handler.update_info
        out = strings['descriptor-date'].format(util.date(update_info["vaccinationsLastUpdated"]))
        for summarize_id, desc, convert in summarize_ids:
            out += desc.format(convert(data[summarize_id]))
        return out

    @staticmethod
    def help(command_list) -> str:
        repl = strings["help-text"]
        for c, d, _ in command_list:
            repl += strings["help-entry-text"].format(command=c, description=d)
        return repl

    @staticmethod
    def start() -> str:
        return strings["start-text"]

    @staticmethod
    def info() -> str:
        return strings["info-text"]

    @staticmethod
    def readme() -> str:
        f = util.get_resource_file("Readme.md", "..")
        s = f.read()
        f.close()
        return s
