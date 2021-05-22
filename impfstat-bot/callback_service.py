import logging

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Updater

import util
from message_generator import MessageGenerator
from plotter import Plotter
from resources import strings, api_key
from update_service import UpdateService


class CallbackService:
    def __init__(self, message_service: MessageGenerator, plot_service: Plotter, update_service: UpdateService):
        self.message_service: MessageGenerator = message_service
        self.plot_service: Plotter = plot_service
        self.update_service: UpdateService = update_service
        self.updater: Updater = None
        # Whitelist jener leute, die die DSGVO akzeptiert haben
        self.whitelist = util.read_json_file("whitelist.json")["list"]

    def get_callback(self, command_type: str, resp_id: str):
        if command_type == "plot":
            def callback(update: Update, context: CallbackContext):
                self.__send_plot(update, context, resp_id)
        elif command_type == "text":
            def callback(update: Update, context: CallbackContext):
                self.__send_text_id(update, context, resp_id)
        elif command_type == "const-text":
            def callback(update: Update, context: CallbackContext):
                self.__send_const(update, context, resp_id)
        elif command_type == "custom":
            callback = self.__get_custom_callback(resp_id)
        else:
            def callback(update: Update, context: CallbackContext):
                pass
            logging.error("unknown callback-id {}:{}".format(command_type, resp_id))
        return callback

    def __send_const(self, update, context, text_id):
        if not self.__check_whitelist(update):
            return
        if text_id not in strings.keys():
            logging.error("{} is not in strings.json".format(text_id))
            return
        try:
            update.message.reply_text(strings[text_id], parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error("Error in __send_const: {}".format(str(e)))
        util.log_message(update)

    def __get_custom_callback(self, resp_id: str):
        if resp_id == "start":
            return self.__start
        elif resp_id == "subscribe":
            return self.__subscribe
        elif resp_id == "unsubscribe":
            return self.__unsubscribe
        elif resp_id == "accept":
            return self.__akzeptieren
        elif resp_id == "feedback":
            return self.__feedback
        elif resp_id == "privacy-notice":
            return self.__privacy
        elif resp_id == "respond":
            return self.__respond
        else:
            def callback(update: Update, context: CallbackContext):
                pass
            logging.error("unknown callback-id custom:{}".format(resp_id))
            return callback

    @staticmethod
    def error_handler(update, context: CallbackContext):
        """
        der error_handler, der vom Telegram.Updater aufgerufen wird, wenn ein Fehler auftritt
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        """

        logging.warning("An error occured: {}, update: {}".format(context.error, update))

    def unknown_command(self, update: Update, context: CallbackContext):
        """Callback Methode unbekannte Kommandos"""
        text = self.message_service.unknown_command(update.message.text)
        self.__send_text(update, context, text, parse_mode=ParseMode.HTML)

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

    def __send_text_id(self, update: Update, context: CallbackContext, text_id: str) -> None:
        """
        Sendet einen Text als Antwort auf eine Nachricht.
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        :param text_id: Text-ID
        """
        if not self.__check_whitelist(update):
            return
        parse_mode, text = self.message_service.gen_text(text_id)
        try:
            update.message.reply_text(text, parse_mode=parse_mode)
        except Exception as e:
            logging.error("Error in __send_text_id: {}".format(str(e)))
        util.log_message(update)

    def __send_text(self, update: Update, context: CallbackContext, text, parse_mode=None) -> None:
        """
        Sendet einen Text als Antwort auf eine Nachricht.
        :param update: Nachrichtenupdate
        :param context: Nachrichtencontext
        :param text_id: Text-ID
        """
        if not self.__check_whitelist(update):
            return
        try:
            update.message.reply_text(text, parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e:
            logging.error("Error in __send_text_id: {}".format(str(e)))
        util.log_message(update)

    def __start(self, update: Update, context: CallbackContext):
        """Callback Methode für /start"""
        if not self.__check_whitelist(update):
            return
        repl = strings["start-text"].format(name=update.effective_chat.first_name)
        self.__send_text(update, context, repl)

    def __akzeptieren(self, update: Update, context: CallbackContext):
        """Callback Methode für /akzeptieren - Fügt Nutzer zur DSGVO-Whitelist hinzu"""
        if update.effective_chat.id not in self.whitelist:
            self.whitelist.append(update.effective_chat.id)
            util.write_json_file({"list": self.whitelist}, "whitelist.json")
            self.__start(update, context)

    def __subscribe(self, update: Update, context: CallbackContext):
        """Callback Methode für /abonnieren"""
        if not self.__check_whitelist(update):
            return
        repl = self.update_service.subscribe(update)
        self.__send_text(update, context, repl)

    def __unsubscribe(self, update: Update, context: CallbackContext):
        """Callback Methode für /deabonnieren"""
        if not self.__check_whitelist(update):
            return
        repl = self.update_service.unsubscribe(update)
        self.__send_text(update, context, repl)

    def __feedback(self, update: Update, context: CallbackContext):
        """Callback Methode für /feedback"""
        if not self.__check_whitelist(update):
            return
        feedback_text = update.message.text
        if len(feedback_text) > len("/feedback "):
            message_text = strings["feedback-admin-text"].format(username=str(update.message.chat.username),
                                                                 feedback=feedback_text,
                                                                 user_id=str(update.message.chat.id))
            self.updater.bot.send_message(api_key["admin-id"], message_text, parse_mode=ParseMode.HTML)

            repl = strings["feedback-text"]
        else:
            repl = strings["feedback-short-text"]
        self.__send_text(update, context, repl, parse_mode=ParseMode.HTML)

    @staticmethod
    def __privacy(update: Update, context: CallbackContext):
        text = util.file_to_string("privacy.html")
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    def __respond(self, update: Update, context: CallbackContext):
        if str(update.message.chat.id) == api_key["admin-id"]:
            msg = update.message.text.split()
            if len(msg) < 3:
                update.message.reply_text("to short")
                return
            target_id = msg[1]
            text = " ".join(msg[2:])
            try:
                self.updater.bot.send_message(target_id, text)
            except Exception as e:
                update.message.reply_text(str(e))
        else:
            update.message.reply_text("unauthorized")

