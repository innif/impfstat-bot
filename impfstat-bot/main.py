import logging
import threading
import time

from telegram.ext import Updater, CommandHandler, StringRegexHandler, MessageHandler, Filters

import util
from callback_service import CallbackService
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
callback_service = CallbackService(mail_man, harry_plotter, update_service)

strings = util.read_json_file("strings.json")  # Strings einlesen
conf = util.read_json_file("config.json")  # config einlesen


def update_service_call():
    """
    Diese Methode ruft in regelmäßigen Abständen (5min)
    """
    update_service.update(updater)
    threading.Timer(conf["update-service-frequency"]*60, update_service_call).start()


# die Funktionen inklusive string.json-Deskriptoren, die der Bot anbietet
functions = [
    ('7-day-avg', callback_service.send_avg),
    ('daily', callback_service.send_daily),
    ('total', callback_service.send_sum),
    ('prognosis', callback_service.prognosis),
    ('numbers', callback_service.numbers),
    ('inst-daily', callback_service.send_institution_daily),
    ('inst-total', callback_service.send_institution_total),
    ('inst-avg', callback_service.send_institution_avg),
    ('pie', callback_service.send_pie_plot),
    ('subscribe', callback_service.subscribe),
    ('unsubscribe', callback_service.unsubscribe),
    ('info', callback_service.info),
    ('help', callback_service.help_command)]
unlisted_commands = [
    ("start", callback_service.start),
    ("akzeptieren", callback_service.akzeptieren),
    ("datenschutzerklaerung", callback_service.datenschutz),
    ()
]

# kommandos,beschreibung,callback-funktion als Tupel in Listen packen
c_strings = strings["commands"]
commands = [(c_strings[s]["command"], c_strings[s]["description"], f) for s, f in functions]
mail_man.available_commands = commands

updater = Updater(util.get_apikey())

# kommandos binden
for command, _, fun in commands:
    updater.dispatcher.add_handler(CommandHandler(command, fun))
for command, fun in unlisted_commands:
    updater.dispatcher.add_handler(CommandHandler(command, fun))
updater.dispatcher.add_handler(MessageHandler(Filters.text, callback_service.unknown_command))
updater.dispatcher.add_error_handler(callback_service.error_handler)

# kommandoliste bereitstellen
updater.bot.set_my_commands([(c, d) for c, d, _ in commands])

if __name__ == '__main__':
    update_service_call()
    updater.start_polling()
    updater.idle()
