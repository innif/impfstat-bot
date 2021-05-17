import logging
from telegram import Update
from telegram.ext import Updater

import util
from data_handler import DataHandler
from message_generator import MessageGenerator

strings = util.read_json_file("strings.json")


class UpdateService:
    def __init__(self, data_handler: DataHandler, message_generator: MessageGenerator):
        self.data_handler = data_handler
        self.message_generator = message_generator
        self.subscriptions = util.read_json_file("subscribers.json")
        self.last_update = util.read_json_file("last-update.json")

    def subscribe(self, update: Update, command="zahlen") -> str:
        chat_id: str = str(update.effective_chat.id)
        if chat_id not in self.subscriptions.keys():
            self.subscriptions[chat_id] = []

        if command in self.subscriptions[chat_id]:
            return strings["already-sub-text"]
        else:
            self.subscriptions[chat_id].append(command)
            self.__write_json()
            return strings["success-sub-text"]

    def unsubscribe(self, update: Update, command="zahlen"):
        chat_id: str = str(update.effective_chat.id)
        if chat_id not in self.subscriptions.keys():
            return strings["already-unsub-text"]

        if command in self.subscriptions[chat_id]:
            assert isinstance(self.subscriptions[chat_id], list)
            self.subscriptions[chat_id].remove(command)
            self.__write_json()
            return strings["success-unsub-text"]
        else:
            return strings["already-unsub-text"]

    def update(self, updater: Updater):
        logging.info("update-service update")
        self.data_handler.update()
        if self.last_update["vaccinationsLastUpdated"] != self.data_handler.update_info["vaccinationsLastUpdated"]:
            logging.info("new Data available")
            self.last_update = self.data_handler.update_info.copy()
            util.write_json_file(self.last_update, "last-update.json")
            msg = self.message_generator.summarize()
            msg = strings["auto-update-text"].format(msg)
            for chat_id in self.subscriptions.keys():
                if "zahlen" in self.subscriptions[chat_id]:
                    try:
                        updater.bot.send_message(chat_id, msg, parse_mode="markdown")
                    except Exception as e:
                        logging.error(e)

    def __write_json(self):
        try:
            util.write_json_file(self.subscriptions, "subscribers.json")
        except Exception as e:
            logging.error(e)
