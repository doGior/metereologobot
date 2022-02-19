from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, \
    PicklePersistence, Dispatcher, BaseFilter, Handler, Defaults


class TelegramClient:
    """
    Classe che ha lo scopo di semplificare la gestione del client
    """
    __istanza: "TelegramClient" = None  # Istanza della classe

    def __init__(self) -> None:
        """
        Inizializzazione della classe
        """
        bot_token = "<TOKEN>"  # Token dato dalle API di Telegram alla creazione di un bot

        # Istanziazione dell'oggetto che riceverà gli aggiornameti sulle chat
        self.updater = Updater(token=bot_token, use_context=True,
                               defaults=Defaults(parse_mode=ParseMode.MARKDOWN),
                               persistence=PicklePersistence("data"))

        # Istanziazione dell'oggetto che contiene i gestori di eventi
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def agg_gest_comandi(self, comando: str, funzione: callable) -> None:
        """
        Aggiunta di un gestore di comandi (es: /start)
        :param comando: Comando da gestire (es: start)
        :param funzione: Funzione da eseguire alla ricezione del comando
        :return: None
        """
        self.dispatcher.add_handler(CommandHandler(comando, funzione))

    def agg_gest_messaggi(self, filtri: BaseFilter, funzione: callable) -> None:
        """
        Aggiunta di un gestore di messaggi
        :param filtri: Filtro per selezionare di che tipo di messaggio occuparsi
        :param funzione: Funzione da eseguire alla ricezione del messaggio ammesso dal filtro
        :return: None
        """
        self.dispatcher.add_handler(MessageHandler(filtri, funzione))

    def agg_gest_pulsanti(self, funzione: callable, pattern: str = None) -> None:
        """
        Aggiunta di un gestore di pulsanti
        :param funzione: Funzione da eseguire alla pressione di un pulsante
        :param pattern: Pattern per selezionare che funzione si occuperà di quel pulsante
        :return: None
        """
        self.dispatcher.add_handler(CallbackQueryHandler(funzione, pattern=pattern))

    def agg_gest_errori(self, funzione: callable) -> None:
        """
        Aggiunta di un gestore di errori
        :param funzione: Funzione da eseguire alla creazione di un errore
        :return: None
        """
        self.dispatcher.add_error_handler(funzione)

    def agg_gest_conversazioni(self, entry_points: list[Handler], states: [object, list[Handler]],
                               fallbacks: list[Handler], *args, **kwargs) -> None:
        """
        Aggiunta di un gestore di conversazioni.
        Utile per l'esecuzione di operazioni che richiedono più messaggi
        :param entry_points: Lista di gestori che fanno inziare la conversazione
        :param states: Dizionario in cui la chiave deve essere l'oggetto restituito dalla funzione precedente e
                        il valore una lista di gestori che restituiscono la chiave successiva
        :param fallbacks: Lista di funzioni che verranno eseguite nel caso in cui la situazione attuale non è
                            prevista da nessun gestore dello stato attuale
        :param args: Eventuali parametri aggiuntivi
        :param kwargs: Eventuali parametri aggiuntivi con valori di default
        :return: None
        """
        conv_handler = ConversationHandler(entry_points, states, fallbacks, *args, **kwargs)
        self.dispatcher.add_handler(conv_handler)

    def agg_gestore(self, gestore: Handler, *args, **kwargs) -> None:
        """
        Aggiunta di un gestore generico
        :param gestore: Gestore da aggiungere
        :param args: Eventuali parametri aggiuntivi
        :param kwargs: Eventuali parametri aggiuntivi con valori di default
        :return: None
        """
        self.dispatcher.add_handler(gestore, *args, **kwargs)

    def rimuovi_gestore(self, gestore: Handler) -> None:
        """
        Rimozione di un gestore dal Dispatcher
        :param gestore: Gestore da rimuovere
        :return: None
        """
        self.dispatcher.remove_handler(gestore)

    def avvia(self) -> None:
        """
        Avvio del bot e ascolto di aggiornamenti da telegram (es: comandi) e dall'host (es: interruzione bot)
        :return: None
        """
        self.updater.start_polling()
        self.updater.idle()

    @staticmethod
    def get_istanza() -> "TelegramClient":
        """
        Restituzione dell'istanza di TelegramClient
        :return: Istanza della classe
        """
        if TelegramClient.__istanza is None:
            TelegramClient.__istanza = TelegramClient()
        return TelegramClient.__istanza

    @staticmethod
    def elimina_istanza() -> None:
        """
        Elimina l'istanza della classe
        :return: None
        """
        TelegramClient.__istanza = None
