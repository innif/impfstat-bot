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

    def sumarize(self) -> str:
        self.data_handler.update()
        data = self.data_handler.newest_data_line
        file_name = conf["data-update-info-filename"]
        update_info = util.read_json_file(file_name, folder="data")
        out = strings['descriptor-date'].format(util.date(update_info["vaccinationsLastUpdated"]))
        for id, descr, convert in summarize_ids:
            out += descr.format(convert(data[id]))
        return out

    def help(self, command_list) -> str:
        repl = strings["help-text"]
        for c, d, _ in command_list:
            repl += strings["help-entry-text"].format(command=c, description=d)
        return repl

    def start(self) -> str:
        return strings["start-text"]

    def info(self) -> str:
        return strings["info-text"]

    def readme(self) -> str:
        return util.get_resource_file("Readme.md", "..").read()
