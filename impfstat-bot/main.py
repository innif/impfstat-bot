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

data_handler = DataHandler()
harry_plotter = Plotter(data_handler)
mail_man = MessageGenerator(data_handler)
update_service = UpdateService(data_handler, mail_man)

strings = util.read_json_file("strings.json")
logging.basicConfig(filename=util.get_resource_file_path("bot{}.log".format(int(time.time())), "logs"),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(filename)s:%(lineno)d - %(message)s')
whitelist = util.read_json_file("whitelist.json")["list"]


def check_whitelist(update: Update):
    if update.effective_chat.id in whitelist:
        return True
    else:
        update.message.reply_text(strings["datenschutz-text"])
        return False


def send_plot(update: Update, context: CallbackContext, plot_type: str):
    if not check_whitelist(update):
        return
    plot_path = harry_plotter.gen_plot(plot_type)
    update.message.reply_photo(open(plot_path, "rb"))
    util.log_message(update)


def send_text(update: Update, context: CallbackContext, text: str, parse_mode="") -> None:
    if not check_whitelist(update):
        return
    if parse_mode != "":
        update.message.reply_text(text, parse_mode=parse_mode)
    else:
        update.message.reply_text(text)
    util.log_message(update)


def error_handler(update, context: CallbackContext):
    logging.warning("An error occured: {}".format(update))


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


def send_institution_avg(update: Update, context: CallbackContext) -> None:
    send_plot(update, context, "inst-avg")


def info(update: Update, context: CallbackContext) -> None:
    repl = mail_man.info()
    send_text(update, context, repl, "markdown")


def help_command(update: Update, context: CallbackContext) -> None:
    repl = mail_man.help(commands)
    send_text(update, context, repl)


def prognosis(update: Update, context: CallbackContext) -> None:
    repl = mail_man.prognosis()
    send_text(update, context, repl)


def numbers(update: Update, context: CallbackContext) -> None:
    repl = mail_man.summarize()
    send_text(update, context, repl, "markdown")


def start(update: Update, context: CallbackContext):
    if not check_whitelist(update):
        return
    repl = mail_man.start(update.effective_chat.first_name)
    send_text(update, context, repl)


def akzeptieren(update: Update, context: CallbackContext):
    if update.effective_chat.id not in whitelist:
        whitelist.append(update.effective_chat.id)
        util.write_json_file({"list": whitelist}, "whitelist.json")
        repl = mail_man.start(update.effective_chat.first_name)
        send_text(update, context, repl)


def datenschutz(update: Update, context: CallbackContext):
    update.message.reply_text(util.file_to_string("Datenschutzerklärung.md"), parse_mode="markdown")


def subscribe(update: Update, context: CallbackContext):
    if not check_whitelist(update):
        return
    repl = update_service.subscribe(update)
    send_text(update, context, repl)


def unsubscribe(update: Update, context: CallbackContext):
    if not check_whitelist(update):
        return
    repl = update_service.unsubscribe(update)
    send_text(update, context, repl)


def update_service_call():
    update_service.update(updater)
    threading.Timer(30.0, update_service_call).start()


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

c_strings = strings["commands"]
commands = [(c_strings[s]["command"], c_strings[s]["description"], f) for s, f in functions]

updater = Updater(util.get_apikey())

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
