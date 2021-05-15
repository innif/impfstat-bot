from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import util
from data_grabber import DataGrabber
from message_generator import MessageGenerator
from plotter import Plotter

data_grabber = DataGrabber()
harry_plotter = Plotter(data_grabber)
mail_man = MessageGenerator(data_grabber)


def send_plot(update: Update, context: CallbackContext, plot_type: str):
    plot_path = harry_plotter.gen_plot(plot_type)
    update.message.reply_photo(open(plot_path, "rb"))
    util.log(update, context)


def send_text(update: Update, context: CallbackContext, text: str) -> None:
    update.message.reply_text(text)
    util.log(update, context)


def error_handler(update, context: CallbackContext):
    util.log(None, context, "ERR")


def send_avg(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "avg")


def send_daily(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "daily")


def send_sum(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "sum")


def send_institution_daily(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "institution")


def send_institution_total(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "inst-sum")


def help(update: Update, context: CallbackContext) -> None:
    repl = mail_man.help(commands)
    send_text(update, context, repl)


def prognosis(update: Update, context: CallbackContext) -> None:
    repl = mail_man.prognosis()
    send_text(update, context, repl)


def numbers(update: Update, context: CallbackContext) -> None:
    repl = mail_man.sumarize()
    send_text(update, context, repl)


def say_hi(update: Update, context: CallbackContext):
    repl = mail_man.start()
    send_text(update, context, repl)


commands = [
    ("7_tage_mittel",   "Liefert eine Grafik der täglich verabreichten Impfdosen mit einem 7-Tage Mittelwert.", send_avg),
    ('dosen_taeglich',  "Liefert eine Grafik der täglich verimpften Dosen.", send_daily),
    ('dosen_summiert',  "Liefert eine Grafik der insgesamt verimpften Dosen.", send_sum),
    ('prognose',        "Gibt an, wie lange es bei dem Aktuellen Impftempo bräuchte, 70% der Bevölkerung zu impfen.",
     prognosis),
    ('zahlen',          "Gibt eine Übersicht der wesentlichen Kennzahlen aus.", numbers),
    ('einrichtung',     "Liefert eine Grafik der täglich verimpften Dosen nach Einrichtung", send_institution_daily),
    ('einrichtung_summiert', "Liefert eine Grafik der summierten verimpften Dosen nach Einrichtung",
     send_institution_total),
    ('help',            "Übersicht aller Befehle", help), ]

updater = Updater(util.get_apikey())

for command, _, fun in commands:
    updater.dispatcher.add_handler(CommandHandler(command, fun))
updater.dispatcher.add_handler(CommandHandler("start", say_hi))
updater.dispatcher.add_error_handler(error_handler)
updater.bot.set_my_commands([(c, d) for c, d, _ in commands])

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
