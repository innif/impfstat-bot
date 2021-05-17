import logging
import threading
import time

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import util
from data_handler import DataHandler
from message_generator import MessageGenerator
from plotter import Plotter
from update_service import UpdateService

# Logging-Format einstellen
logging.basicConfig(filename=util.get_resource_file_path("bot{}.log".format(int(time.time())), "logs"),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(filename)s:%(lineno)d - %(message)s')

data_handler = DataHandler()  # ruft de Daten ab und berechnet Werte
harry_plotter = Plotter(data_handler)  # der Auserwählte. Nur er kann plotten
mail_man = MessageGenerator(data_handler)  # der mail_man generiert die Textnachrichten
update_service = UpdateService(data_handler, mail_man)  # service für die täglichen Updates

strings = util.read_json_file("strings.json")  # Strings einlesen
conf = util.read_json_file("config.json")  # config einlesen
whitelist = util.read_json_file("whitelist.json")["list"]  # Whitelist jener leute, die die DSGVO akzeptiert haben


def check_whitelist(update: Update):
    """
    Prüft, ob der Sender einer Nachricht auf der DSGVO-Whitelist steht.
    Sendet andernfalls die Bitte, die Datenschutzerklärung zu akzeptieren
    :param update: Nachrichtenupdate
    :return: True, wenn nutzer auf der Whitelist
    """
    if update.effective_chat.id in whitelist:
        return True
    else:
        update.message.reply_text(strings["datenschutz-text"])
        return False


def send_plot(update: Update, context: CallbackContext, plot_type: str) -> None:
    """
    Sendet einen plot als Antwort auf eine Nachricht.
    :param update: Nachrichtenupdate
    :param context: Nachrichtencontext
    :param plot_type: art des Plots gemäß der Klasse Plotter
    """
    if not check_whitelist(update):
        return
    plot_path = harry_plotter.gen_plot(plot_type)
    update.message.reply_photo(open(plot_path, "rb"))
    util.log_message(update)


def send_text(update: Update, context: CallbackContext, text: str, parse_mode="") -> None:
    """
    Sendet einen Text als Antwort auf eine Nachricht.
    :param update: Nachrichtenupdate
    :param context: Nachrichtencontext
    :param text: Text
    :param parse_mode: "", "markdown" oder "html"
    """
    if not check_whitelist(update):
        return
    if parse_mode != "":
        update.message.reply_text(text, parse_mode=parse_mode)
    else:
        update.message.reply_text(text)
    util.log_message(update)


def error_handler(update, context: CallbackContext):
    """
    der error_handler, der vom Telegram.Updater aufgerufen wird, wenn ein Fehler auftritt
    :param update: Nachrichtenupdate
    :param context: Nachrichtencontext
    """
    logging.warning("An error occured: {}".format(update))


def send_avg(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /7_tage_mittel"""
    send_plot(update, context, "avg")


def send_daily(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /dosen_taeglich"""
    send_plot(update, context, "daily")


def send_sum(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /dosen_summiert"""
    send_plot(update, context, "sum")


def send_institution_daily(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /einrichtung"""
    send_plot(update, context, "institution")


def send_institution_total(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /einrichtung_summiert"""
    send_plot(update, context, "inst-sum")


def send_institution_avg(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /einrichtung_mittel"""
    send_plot(update, context, "inst-avg")


def info(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /info"""
    repl = mail_man.info()
    send_text(update, context, repl, "markdown")


def help_command(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /help"""
    repl = mail_man.help(commands)
    send_text(update, context, repl)


def prognosis(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /prognose"""
    repl = mail_man.prognosis()
    send_text(update, context, repl)


def numbers(update: Update, context: CallbackContext) -> None:
    """Callback Methode für /zahlen"""
    repl = mail_man.summarize()
    send_text(update, context, repl, "markdown")


def start(update: Update, context: CallbackContext):
    """Callback Methode für /start"""
    if not check_whitelist(update):
        return
    repl = mail_man.start(update.effective_chat.first_name)
    send_text(update, context, repl)


def akzeptieren(update: Update, context: CallbackContext):
    """Callback Methode für /akzeptieren - Fügt Nutzer zur DSGVO-Whitelist hinzu"""
    if update.effective_chat.id not in whitelist:
        whitelist.append(update.effective_chat.id)
        util.write_json_file({"list": whitelist}, "whitelist.json")
        repl = mail_man.start(update.effective_chat.first_name)
        send_text(update, context, repl)


def datenschutz(update: Update, context: CallbackContext):
    """Callback Methode für /datenschutzerklaerung"""
    update.message.reply_text(util.file_to_string("Datenschutzerklärung.md"), parse_mode="markdown")


def subscribe(update: Update, context: CallbackContext):
    """Callback Methode für /abonnieren"""
    if not check_whitelist(update):
        return
    repl = update_service.subscribe(update)
    send_text(update, context, repl)


def unsubscribe(update: Update, context: CallbackContext):
    """Callback Methode für /deabonnieren"""
    if not check_whitelist(update):
        return
    repl = update_service.unsubscribe(update)
    send_text(update, context, repl)


def update_service_call():
    """
    Diese Methode ruft in regelmäßigen Abständen (5min)
    """
    update_service.update(updater)
    threading.Timer(conf["update-service-frequency"]*60, update_service_call).start()


# die Funktionen inklusive string.json-Deskriptoren, die der Bot anbietet
functions = [
    ('7-day-avg', send_avg),
    ('daily', send_daily),
    ('total', send_sum),
    ('prognosis', prognosis),
    ('numbers', numbers),
    ('inst-daily', send_institution_daily),
    ('inst-total', send_institution_total),
    ('inst-avg', send_institution_avg),
    ('subscribe', subscribe),
    ('unsubscribe', unsubscribe),
    ('info', info),
    ('help', help_command)]

# kommandos,beschreibung,callback-funktion als Tupel in Listen packen
c_strings = strings["commands"]
commands = [(c_strings[s]["command"], c_strings[s]["description"], f) for s, f in functions]

updater = Updater(util.get_apikey())

# kommandos binden
for command, _, fun in commands:
    updater.dispatcher.add_handler(CommandHandler(command, fun))
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("akzeptieren", akzeptieren))
updater.dispatcher.add_handler(CommandHandler("datenschutzerklaerung", datenschutz))
updater.dispatcher.add_error_handler(error_handler)
updater.bot.set_my_commands([(c, d) for c, d, _ in commands])

if __name__ == '__main__':
    update_service_call()
    updater.start_polling()
    updater.idle()
