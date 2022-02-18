from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler,\
    PicklePersistence, Dispatcher


class TelegramClient:
    __instance = None

    def __init__(self):
        bot_token = "<TOKEN>"
        self.updater = Updater(token=bot_token, use_context=True,
                               persistence=PicklePersistence("data"))
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def add_command_handler(self, command, function):
        new_handler = CommandHandler(command, function)
        self.dispatcher.add_handler(new_handler)

    def add_message_handler(self, filters, function):
        new_handler = MessageHandler(filters, function)
        self.dispatcher.add_handler(new_handler)

    def add_callback_query_handler(self, function, pattern=None):
        self.dispatcher.add_handler(CallbackQueryHandler(function, pattern=pattern))

    def add_error_handler(self, function):
        self.dispatcher.add_error_handler(function)

    def add_conversation_handler(self, entry_points, states, fallbacks, *args, **kwargs):
        conv_handler = ConversationHandler(entry_points, states, fallbacks, *args, **kwargs)
        self.dispatcher.add_handler(conv_handler)

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def remove_handler(self, handler):
        self.dispatcher.remove_handler(handler)

    def start_and_idle(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        self.updater.stop()

    @staticmethod
    def get_instance():
        if TelegramClient.__instance is None:
            TelegramClient.__instance = TelegramClient()
        return TelegramClient.__instance

    @staticmethod
    def delete_instance():
        TelegramClient.__instance = None
