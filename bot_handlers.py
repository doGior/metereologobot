from datetime import datetime

from telegram.ext import ConversationHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
import api_parser
import strings

openweather = api_parser.OpenWeather()


def start(update: Update, context: CallbackContext) -> None:
    """
    Invio messaggio d'inizio
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    # Elenco di pulsanti
    tastiera = [[
        InlineKeyboardButton(strings.plt_cond_att, callback_data=strings.cld_cond_attuali),
        InlineKeyboardButton(strings.plt_previsioni, callback_data=strings.cld_previsioni)],
        [InlineKeyboardButton(strings.plt_impostazioni, callback_data=strings.cld_impostazioni)]]

    # Serializzazione dei pulsanti
    reply_markup = InlineKeyboardMarkup(tastiera)

    # Set variabile utente
    context.user_data[strings.usr_indice_giorni] = 0

    # Invio messaggio
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=strings.msg_start.format(username=update.effective_user.username),
                             reply_markup=reply_markup)


def condizioni_attuali(update: Update, context: CallbackContext) -> None:
    """
    Invio delle dati_meteo sulle condizioni meteo attuali
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    query = update.callback_query
    tastiera = [[InlineKeyboardButton(strings.msg_icona_indietro,
                                      callback_data=strings.cld_indietro + strings.cld_allinizio)]]
    reply_markup = InlineKeyboardMarkup(tastiera)

    dati_utente = context.user_data
    uni_misura = dati_utente.get(strings.usr_misura, strings.cld_metrico)
    temp_unit = strings.msg_simb_fahrenheit if uni_misura == strings.cld_imperiale else strings.msg_simb_celsius
    try:
        # Ottenimento dati salvati in precedenza
        lat = dati_utente[strings.usr_lat]
        lon = dati_utente[strings.usr_lon]
        citta = dati_utente[strings.usr_citta]
    except KeyError:
        # Segnalazione dati non salvati in precedenza
        query.edit_message_text(text=strings.msg_non_loc, reply_markup=reply_markup)
        return

    dati_meteo = openweather.get_condizioni_attuali(lat, lon, uni_misura)
    messaggio = strings.msg_cond_att.format(citta=citta.upper(),
                                            tempo=dati_meteo['weather'][0]['description'].capitalize(),
                                            temperatura=dati_meteo['main']['temp'],
                                            temp_per=dati_meteo['main']['feels_like'],
                                            temp_uni=temp_unit,
                                            umidita=dati_meteo['main']['humidity'])

    query.edit_message_text(text=messaggio, reply_markup=reply_markup)


def previsioni(update: Update, context: CallbackContext) -> None:
    """
    Invio delle informazioni relative al meteo dei prossimi giorni divise per pagina
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    query = update.callback_query
    tastiera = [
        [InlineKeyboardButton(strings.msg_icona_indietro,
                              callback_data=strings.cld_indietro + strings.cld_dalle_previsioni),
         InlineKeyboardButton(strings.msg_icona_avanti, callback_data=strings.cld_avanti)]]

    reply_markup = InlineKeyboardMarkup(tastiera)

    dati_utente = context.user_data
    uni_misura = dati_utente.get(strings.usr_misura, strings.cld_metrico)
    temp_unit = strings.msg_simb_fahrenheit if uni_misura == strings.cld_imperiale else strings.msg_simb_celsius
    vel_unit = strings.msg_mph if uni_misura == strings.cld_imperiale else strings.msg_kmh

    try:
        lat = dati_utente[strings.usr_lat]
        lon = dati_utente[strings.usr_lon]
        citta = dati_utente[strings.usr_citta]
    except KeyError:
        tastiera[0].pop(1)
        query.edit_message_text(text=strings.msg_non_loc, reply_markup=reply_markup)
        return

    indice_previsioni = dati_utente.get(strings.usr_indice_giorni, 0)
    dati_previsioni = dati_utente.get(strings.usr_previsioni, openweather.get_previsioni(lat, lon, uni_misura))
    context.user_data[strings.usr_previsioni] = dati_previsioni

    # Rimozione pulsante avanti al termine della lista
    if indice_previsioni >= len(dati_previsioni) - 1:
        tastiera[0].pop(1)

    dati_giorno = dati_previsioni[indice_previsioni]

    vento = dati_giorno["wind_speed"] if uni_misura == strings.cld_imperiale else dati_giorno["wind_speed"] * 3.6
    messaggio_formattato = strings.msg_previsione. \
        format(citta=citta.upper(),
               data=datetime.utcfromtimestamp(dati_giorno['dt']).strftime('%d/%m/%Y'),
               alba=datetime.utcfromtimestamp(dati_giorno['sunrise']).strftime('%H:%M'),
               tramonto=datetime.utcfromtimestamp(dati_giorno['sunset']).strftime('%H:%M'),
               temp_min=dati_giorno['temp']['min'],
               temp_max=dati_giorno['temp']['max'],
               temp_unit=temp_unit,
               vento=round(vento, 3),
               vel_unit=vel_unit,
               pressione=dati_giorno['pressure'],
               umidita=dati_giorno['humidity'])

    query.delete_message()
    context.bot.send_message(chat_id=update.effective_chat.id, text=messaggio_formattato, reply_markup=reply_markup)


def prossimo_giorno(update: Update, context: CallbackContext) -> None:
    """
    Prossima pagina delle previsioni
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    dati_utente = context.user_data
    indice_previsioni = dati_utente.get(strings.usr_indice_giorni, 0)
    num_giorni_previsioni = dati_utente.get(strings.usr_previsioni, [])

    # Controllo che l'indice non sia superiore al numero di elementi con i dati delle previsioni
    if indice_previsioni >= len(num_giorni_previsioni) and indice_previsioni > 0:
        return

    indice_previsioni += 1
    context.user_data[strings.usr_indice_giorni] = indice_previsioni
    previsioni(update, context)


def impostazioni(update: Update, context: CallbackContext) -> None:
    """
    Invio del messaggio con le impostazioni
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    tastiera = [[
        InlineKeyboardButton(strings.plt_localita, callback_data=strings.cld_luogo),
        InlineKeyboardButton(strings.plt_misura, callback_data=strings.cld_unita_misura)],
        [InlineKeyboardButton(strings.msg_icona_indietro, callback_data=strings.cld_indietro + strings.cld_allinizio)]]
    query = update.callback_query
    query.edit_message_text(text=strings.msg_mod_imp,
                            reply_markup=InlineKeyboardMarkup(tastiera))


def presentazione_unita_misura(update: Update, context: CallbackContext) -> None:
    """
    Invio del messaggio con le opzioni relative al sistema di misurazione
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    tastiera = [[
        InlineKeyboardButton(strings.plt_metrico, callback_data=strings.cld_sel_unita_misura+strings.cld_metrico),
        InlineKeyboardButton(strings.plt_imperiale, callback_data=strings.cld_sel_unita_misura+strings.cld_imperiale)],
        [InlineKeyboardButton(strings.msg_icona_indietro,
                              callback_data=strings.cld_indietro + strings.cld_alle_impostazioni)]]
    query = update.callback_query
    query.edit_message_text(text=strings.msg_sel_misura,
                            reply_markup=InlineKeyboardMarkup(tastiera))


def selezione_unita_misura(update: Update, context: CallbackContext) -> None:
    """
    Conferma selezione sistema di misurazione e aggiornamento dati
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    dati = update.callback_query.data
    uni_misura = dati[dati.index(":") + 1:]
    context.user_data[strings.usr_misura] = uni_misura
    query = update.callback_query
    query.edit_message_text(text=strings.msg_op_agg)
    start(update, context)


def richiesta_localita(update: Update, context: CallbackContext) -> int:
    """
    Richiesta della località di cui sapere il meteo
    (Punto di partenza del gestore della conversazione)
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    tastiera = [[InlineKeyboardButton(strings.msg_icona_indietro,
                                      callback_data=strings.cld_indietro_alle_impostazioni)]]
    query = update.callback_query
    query.edit_message_text(text=strings.msg_dom_citta,
                            reply_markup=InlineKeyboardMarkup(tastiera))
    return 0


def presentazione_localita(update: Update, context: CallbackContext) -> int:
    """
    Presentazione località trovate dall'API
    (Stato 0 del gestore delle conversazioni)
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    citta = update.message.text
    risultati = openweather.cerca_luogo(citta)

    tastiera = [InlineKeyboardButton(strings.plt_luogo.format(citta=i['name'], paese=i['country']),
                                     callback_data=f"{strings.cld_luogo_presentato}{i['name']}|{i['lat']}:{i['lon']}")
                for i in risultati]

    tastiera = [[i] for i in tastiera]
    tastiera.append([InlineKeyboardButton(strings.msg_icona_indietro,
                                          callback_data=strings.cld_indietro_alle_impostazioni)])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=strings.msg_sel_citta,
                             reply_markup=InlineKeyboardMarkup(tastiera))
    return 1


def conferma_selezione_localita(update: Update, context: CallbackContext) -> int:
    """
    Conferma della selezione della località e aggiornamento dei dati
    (Stato 1 del gestore delle conversazioni)
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    dati = update.callback_query.data
    citta = dati[dati.index(":") + 1:dati.rindex("|")]
    lat = dati[dati.rindex("|") + 1:dati.rindex(":")]
    lon = dati[dati.rindex(":") + 1:]

    context.user_data[strings.usr_lat] = lat
    context.user_data[strings.usr_lon] = lon
    context.user_data[strings.usr_citta] = citta

    query = update.callback_query
    query.edit_message_text(text=strings.msg_citta_selezionata)

    start(update, context)

    # Fine conversazione
    return ConversationHandler.END


def indietro(update: Update, context: CallbackContext) -> None:
    """
    Implementazione del pulsante indietro nelle varie schermate
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    query = update.callback_query

    dati = query.data
    dati = dati[dati.index(":") + 1:]

    if dati == strings.cld_allinizio:  # Ritorno all'inizio
        query.delete_message()
        start(update, context)
    elif dati == strings.cld_alle_impostazioni:  # Ritorno alle impostazioni
        indietro_alle_impostazioni(update, context)
        return
    elif dati == strings.cld_dalle_previsioni:  # Ritorno alla pagina precedente delle previsioni
        indice_previsioni = context.user_data.get(strings.usr_indice_giorni, 0)
        if indice_previsioni == 0:
            query.delete_message()
            start(update, context)
        else:
            indice_previsioni -= 1
            context.user_data[strings.usr_indice_giorni] = indice_previsioni
            previsioni(update, context)


def indietro_alle_impostazioni(update: Update, context: CallbackContext) -> int:
    """
    Implementazione del tasto indietro nel gestore delle conversazioni
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    impostazioni(update, context)
    return ConversationHandler.END


def error(update: Update, context: CallbackContext) -> int:
    """
    Avviso di errori
    :param update: evento che ha fatto partire la funzione
    :param context: oggetto con informazioni sul contesto (es: dati utente)
    :return: None
    """
    update.callback_query.answer(strings.msg_errore, show_alert=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=strings.msg_errore)
    context.user_data[strings.usr_indice_giorni] = 0
    start(update, context)
    if update.message is not None:
        context.bot.delete_message(update.message.message_id)
    return -1
