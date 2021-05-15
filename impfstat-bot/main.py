from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import util
from data_grabber import DataGrabber
from message_generator import MessageGenerator
from plotter import Plotter

data_grabber = DataGrabber()
harry_plotter = Plotter(data_grabber)
mail_man = MessageGenerator(data_grabber)

strings = util.get_conf_file("strings.json")


def send_plot(update: Update, context: CallbackContext, plot_type: str):
    plot_path = harry_plotter.gen_plot(plot_type)
    update.message.reply_photo(open(plot_path, "rb"))
    util.log(update, context)


def send_text(update: Update, context: CallbackContext, text: str, parse_mode="") -> None:
    if parse_mode != "":
        update.message.reply_text(text, parse_mode=parse_mode)
    else:
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


def info(update: Update, context: CallbackContext) -> None:
    repl = mail_man.info()
    send_text(update, context, repl, "markdown")


def help(update: Update, context: CallbackContext) -> None:
    repl = mail_man.help(commands)
    send_text(update, context, repl)


def prognosis(update: Update, context: CallbackContext) -> None:
    repl = mail_man.prognosis()
    send_text(update, context, repl)


def numbers(update: Update, context: CallbackContext) -> None:
    repl = mail_man.sumarize()
    send_text(update, context, repl, "markdown")


def say_hi(update: Update, context: CallbackContext):
    repl = mail_man.start()
    send_text(update, context, repl)

functions = [
    ('7-day-avg', send_avg),
    ('daily', send_daily),
    ('total', send_sum),
    ('prognosis', prognosis),
    ('numbers', numbers),
    ('inst-daily', send_institution_daily),
    ('inst-total', send_institution_total),
    ('info', info),
    ('help', help)]

c_strings = strings["commands"]
commands = [(c_strings[s]["command"], c_strings[s]["description"], f) for s, f in functions]

updater = Updater(util.get_apikey())

for command, _, fun in commands:
    updater.dispatcher.add_handler(CommandHandler(command, fun))
updater.dispatcher.add_handler(CommandHandler("start", say_hi))
updater.dispatcher.add_error_handler(error_handler)
updater.bot.set_my_commands([(c, d) for c, d, _ in commands])

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
