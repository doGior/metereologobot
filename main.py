from telegram.ext import CallbackQueryHandler, MessageHandler, Filters
import logging

import telegram_client
import bot_handlers


def main():
    client = telegram_client.TelegramClient.get_instance()

    client.add_command_handler('start', bot_handlers.start)
    client.add_error_handler(bot_handlers.error)
    client.add_callback_query_handler(bot_handlers.current_conditions, "curr_con")
    client.add_callback_query_handler(bot_handlers.forecast, "forecast")
    client.add_callback_query_handler(bot_handlers.preferences, "preferences")

    client.add_callback_query_handler(bot_handlers.present_measure_unit, "unit_select")
    client.add_callback_query_handler(bot_handlers.select_measure_unit, "unit:")
    client.add_callback_query_handler(bot_handlers.back, "back:")
    client.add_callback_query_handler(bot_handlers.next_day, "next")

    client.add_conversation_handler(
        entry_points=[CallbackQueryHandler(bot_handlers.ask_for_location, pattern="location")],
        states={
            0: [MessageHandler(Filters.text & (~ Filters.command), bot_handlers.present_locations)],
            1: [CallbackQueryHandler(bot_handlers.location_selected, pattern="loc:")],
        },
        fallbacks=[CallbackQueryHandler(bot_handlers.back_to_pref, pattern="back_to_preferences")],

        per_message=False,
        per_user=True,
        per_chat=True
    )

    client.start_and_idle()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    main()
