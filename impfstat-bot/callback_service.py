import logging
from random import random

from telegram import Update
from telegram.ext import CallbackContext

import util
from message_generator import MessageGenerator
from plotter import Plotter
from update_service import UpdateService

strings = util.read_json_file("strings.json")  # Strings einlesen


class CallbackService:
    def __init__(self, message_service: MessageGenerator, plot_service: Plotter, update_service: UpdateService):
        self.message_service: MessageGenerator = message_service
        self.plot_service: Plotter = plot_service
        self.update_service: UpdateService = update_service
        # Whitelist jener leute, die die DSGVO akzeptiert haben
        self.whitelist = util.read_json_file("whitelist.json")["list"]

    def __check_whitelist(self, update: Update):
        """
        Prüft, ob der Sender einer Nachricht auf der DSGVO-Whitelist steht.
        Sendet andernfalls die Bitte, die Datenschutzerklärung zu akzeptieren
        :param update: Nachrichtenupdate
        :return: True, wenn nutzer auf der Whitelist
        """
        if update.effective_chat.id in self.whitelist:
            return True
        else:
            update.message.reply_text(strings["datenschutz-text"])
            return False

    def __send_plot(self, update: Update, context: CallbackContext, plot_type: str) -> None:
        """
        Sendet einen plot als Antwort auf eine Nachricht.
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        :param plot_type: art des Plots gemäß der Klasse Plotter
        """
        if not self.__check_whitelist(update):
            return
        plot_path = self.plot_service.gen_plot(plot_type)
        if plot_path is not None:
            update.message.reply_photo(open(plot_path, "rb"))
        util.log_message(update)

    def __send_text(self, update: Update, context: CallbackContext, text: str, parse_mode="") -> None:
        """
        Sendet einen Text als Antwort auf eine Nachricht.
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        :param text: Text
        :param parse_mode: "", "markdown" oder "html"
        """
        if not self.__check_whitelist(update):
            return
        if parse_mode != "":
            update.message.reply_text(text, parse_mode=parse_mode)
        else:
            update.message.reply_text(text)
        util.log_message(update)

    @staticmethod
    def error_handler(update, context: CallbackContext):
        """
        der error_handler, der vom Telegram.Updater aufgerufen wird, wenn ein Fehler auftritt
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        """
        logging.warning("An error occured: {}".format(update))

    def send_avg(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /7_tage_mittel"""
        self.__send_plot(update, context, "avg")

    def send_pie_plot(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /torte"""
        self.__send_plot(update, context, "pie")

    def send_daily(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /dosen_taeglich"""
        self.__send_plot(update, context, "daily")

    def send_sum(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /dosen_summiert"""
        self.__send_plot(update, context, "sum")

    def send_institution_daily(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /einrichtung"""
        self.__send_plot(update, context, "institution")

    def send_institution_total(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /einrichtung_summiert"""
        self.__send_plot(update, context, "inst-sum")

    def send_institution_avg(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /einrichtung_mittel"""
        self.__send_plot(update, context, "inst-avg")

    def info(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /info"""
        self.__send_text(update, context, strings["info-text"], "markdown")

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /help"""
        repl = self.message_service.help()
        self.__send_text(update, context, repl)

    def prognosis(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /prognose"""
        repl = self.message_service.prognosis()
        self.__send_text(update, context, repl)

    def numbers(self, update: Update, context: CallbackContext) -> None:
        """Callback Methode für /zahlen"""
        repl = self.message_service.summarize()
        self.__send_text(update, context, repl, "markdown")

    def start(self, update: Update, context: CallbackContext):
        """Callback Methode für /start"""
        if not self.__check_whitelist(update):
            return
        repl = strings["start-text"].format(name=update.effective_chat.first_name)
        self.__send_text(update, context, repl)

    def akzeptieren(self, update: Update, context: CallbackContext):
        """Callback Methode für /akzeptieren - Fügt Nutzer zur DSGVO-Whitelist hinzu"""
        if update.effective_chat.id not in self.whitelist:
            self.whitelist.append(update.effective_chat.id)
            util.write_json_file({"list": self.whitelist}, "whitelist.json")
            self.start(update, context)

    def unknown_command(self, update: Update, context: CallbackContext):
        """Callback Methode unbekannte Kommandos"""
        text = self.message_service.unknown_command()
        self.__send_text(update, context, text)

    @staticmethod
    def datenschutz(update: Update, context: CallbackContext):
        """Callback Methode für /datenschutzerklaerung"""
        update.message.reply_text(util.file_to_string("Datenschutzerklärung.md"), parse_mode="markdown")

    def subscribe(self, update: Update, context: CallbackContext):
        """Callback Methode für /abonnieren"""
        if not self.__check_whitelist(update):
            return
        repl = self.update_service.subscribe(update)
        self.__send_text(update, context, repl)

    def unsubscribe(self, update: Update, context: CallbackContext):
        """Callback Methode für /deabonnieren"""
        if not self.__check_whitelist(update):
            return
        repl = self.update_service.unsubscribe(update)
        self.__send_text(update, context, repl)
