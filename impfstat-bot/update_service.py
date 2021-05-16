from telegram import Update

import util

strings = util.read_json_file("strings.json")


class UpdateService:
    def __init__(self):
        self.subscriptions = util.read_json_file("subscribers.json")

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

    def __write_json(self):
        util.write_json_file(self.subscriptions, "subscribers.json")
