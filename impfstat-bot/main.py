import logging
import threading
import time

from telegram.ext import Updater, CommandHandler, StringRegexHandler, MessageHandler, Filters

import util
from callback_service import CallbackService
from data_handler import DataHandler
from message_generator import MessageGenerator
from plotter import Plotter
from resources import conf, commands
from update_service import UpdateService

# Logging-Format einstellen
logging_format = '%(asctime)s - %(levelname)s - %(funcName)s - %(filename)s:%(lineno)d - %(message)s'
if util.is_debug():
    logging.basicConfig(level=logging.INFO, format=logging_format)
else:
    logging.basicConfig(filename=util.get_resource_file_path("bot{}.log".format(int(time.time())), "logs"),
                        level=logging.INFO, format=logging_format)
logging.info("start")


def replot_all():
    harry_plotter.delete_plots()
    x = threading.Thread(target=harry_plotter.render_all, daemon=True)
    x.start()


def update_service_call():
    """
    Diese Methode ruft in regelmäßigen Abständen (5min)
    """
    try:
        update_service.update(updater)
    except Exception as e:
        logging.warning("error in update_Service_call: {}".format(str(e)))
    threading.Timer(conf["update-service-frequency"] * 60, update_service_call).start()


data_handler = DataHandler()  # ruft de Daten ab und berechnet Werte
harry_plotter = Plotter(data_handler)  # der Auserwählte. Nur er kann plotten
mail_man = MessageGenerator(data_handler)  # der mail_man generiert die Textnachrichten
update_service = UpdateService(data_handler, mail_man)  # service für die täglichen Updates
callback_service = CallbackService(mail_man, harry_plotter, update_service)
updater = Updater(util.get_apikey())

data_handler.new_data_callback = replot_all
replot_all()

dropdown_commands = []

# kommandos binden
for key in commands.keys():
    command = commands[key]
    callback = callback_service.get_callback(command["type"], command["resp-id"])
    updater.dispatcher.add_handler(CommandHandler(key, callback))
    if command["visible-dropdown"]:
        dropdown_commands.append((key, command["description"]))

updater.dispatcher.add_handler(MessageHandler(Filters.text, callback_service.unknown_command))
updater.dispatcher.add_error_handler(callback_service.error_handler)

# kommandoliste bereitstellen
updater.bot.set_my_commands(dropdown_commands)

callback_service.updater = updater

if __name__ == '__main__':
    update_service_call()
    updater.start_polling()
    updater.idle()
