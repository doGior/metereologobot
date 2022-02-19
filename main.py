from telegram.ext import CallbackQueryHandler, MessageHandler, Filters
import logging

import strings
import telegram_client
import bot_handlers


def main() -> None:
    """
    Metodo principale del bot. Crea il client, ne configura i gestori degli eventi e lo fa partire
    :return: None
    """

    client = telegram_client.TelegramClient.get_istanza()  # Creazione istanza del client

    # Aggiunta gestori di eventi
    client.agg_gest_comandi('start', bot_handlers.start)
    client.agg_gest_errori(bot_handlers.error)
    client.agg_gest_pulsanti(bot_handlers.condizioni_attuali, strings.cld_cond_attuali)
    client.agg_gest_pulsanti(bot_handlers.previsioni, strings.cld_previsioni)
    client.agg_gest_pulsanti(bot_handlers.impostazioni, strings.cld_impostazioni)

    client.agg_gest_pulsanti(bot_handlers.presentazione_unita_misura, strings.cld_unita_misura)
    client.agg_gest_pulsanti(bot_handlers.selezione_unita_misura, strings.cld_sel_unita_misura)
    client.agg_gest_pulsanti(bot_handlers.indietro, strings.cld_indietro)
    client.agg_gest_pulsanti(bot_handlers.prossimo_giorno, strings.cld_avanti)

    # Aggiunta gestore di una conversazione
    client.agg_gest_conversazioni(
        entry_points=[CallbackQueryHandler(bot_handlers.richiesta_localita, pattern=strings.cld_luogo)],
        states={
            0: [MessageHandler(Filters.text & (~ Filters.command), bot_handlers.presentazione_localita)],
            1: [CallbackQueryHandler(bot_handlers.conferma_selezione_localita, pattern=strings.cld_luogo_presentato)],
        },
        fallbacks=[CallbackQueryHandler(bot_handlers.indietro_alle_impostazioni, pattern=strings.cld_indietro_alle_impostazioni)],

        per_message=False,
        per_user=True,
        per_chat=True
    )

    # Inizializzazione
    client.avvia()


if __name__ == "__main__":
    # Log degli errori
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    main()  # Avvio del bot
