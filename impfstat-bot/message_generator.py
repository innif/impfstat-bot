import util
from plotter import Plotter
from data_grabber import DataGrabber

summarize_ids = [
    ('date', "Datum: ", util.date),
    ('dosen_kumulativ', "Insgesamt verabreichte Dosen: ", util.to_mio),
    ('dosen_differenz_zum_vortag', "Dosen differenz zum Vortag: ", util.dec_points),
    ('impf_quote_erst', "Impfquote Erstimpfung: ", util.to_percent),
    ('impf_quote_voll', "Impfquote vollständig geimpft: ", util.to_percent),
]

consts = util.get_conf_file("constants.json")

class MessageGenerator:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def prognosis(self, quote=.7):
        self.data_handler.update()
        data, n_samples = self.data_handler.data, self.data_handler.data_len
        doses_given = int(data["dosen_kumulativ"][n_samples - 1])
        doses_per_day = sum(int(s) for s in data["dosen_differenz_zum_vortag"][n_samples - 7:n_samples]) / 7
        doses_per_vacc = consts["doses_per_vacc"]
        doses_needed = (quote * doses_per_vacc * consts["population"]) - doses_given
        time_needed = doses_needed / doses_per_day
        months = int(time_needed / 30)
        days = int(time_needed % 30)
        return "{:2.0f}% der Bevölkerung könnten bei dem momentanen Tempo nach {} Monaten und {} Tagen vollständig geimpft sein.".format(
            quote * 100, months, days)

    def sumarize(self):
        self.data_handler.update()
        data = self.data_handler.newest_data_line
        out = ""
        for id, descr, convert in summarize_ids:
            out += descr + convert(data[id])
            out += "\n"
        return out

    def help(self, command_list):
        repl = "Du kannst zwischen folgenden Komandos wählen:\n"
        for c, d, _ in command_list: repl += "/{} - {}\n".format(c, d)
        return repl

    def start(self):
        return "Moin! Ich möchte dir helfen, einen Überblick über die aktuellen Impfstatistiken zu bekommen. Für eine Auflistung aller Befehle schreibe /help"
