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
commands = util.read_json_file("commands.json")  # config einlesen


def update_service_call():
    """
    Diese Methode ruft in regelmäßigen Abständen (5min)
    """
    update_service.update(updater)
    threading.Timer(conf["update-service-frequency"]*60, update_service_call).start()


updater = Updater(util.get_apikey())

dropdown_commands = []

# kommandos binden
for key in commands.keys():
    command = commands[key]
    callback = callback_service.get_callback(command["type"], command["resp-id"])
    updater.dispatcher.add_handler(CommandHandler(key, callback))
    if command["visible-dropdown"]:
        dropdown_commands.append((key, command["description"]))
    if command["visible-help"]:
        mail_man.available_commands.append((key, command["description"]))

updater.dispatcher.add_handler(MessageHandler(Filters.text, callback_service.unknown_command))
updater.dispatcher.add_error_handler(callback_service.error_handler)

# kommandoliste bereitstellen
updater.bot.set_my_commands(dropdown_commands)

if __name__ == '__main__':
    update_service_call()
    updater.start_polling()
    updater.idle()
