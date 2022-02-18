from datetime import datetime

from telegram.ext import ConversationHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext
import api_parser

openweather = api_parser.OpenWeather()
curr_forecast_index = 0  # TODO salvarlo in user_data
messages = []  # TODO salvarlo in user_data

# TODO Refactor generale
# TODO tradurre tutto in italiano


def start(update: Update, context: CallbackContext):
    keyboard = [[
        InlineKeyboardButton("Condizioni attuali", callback_data='curr_con'),
        InlineKeyboardButton("Previsioni", callback_data='forecast'),
    ], [InlineKeyboardButton("Impostazioni", callback_data='preferences')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Ciao @{update.effective_user.username}, come posso esserti utile?",
                             reply_markup=reply_markup)


def current_conditions(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("◀", callback_data="back:to_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    data = context.user_data
    unit = data.get("measure_unit", "metric")
    temp_unit = "F" if unit == "imperial" else "C"
    try:
        data: dict = context.user_data
        lat = data["location_lat"]
        lon = data["location_lon"]
        unit = data.get("measure_unit", "metric")
        name = data["name"]

        message_dict = openweather.get_current_conditions(lat, lon, unit)
        message = f"*{name.upper()}*\n\n" \
                  f"{message_dict['weather'][0]['description'].capitalize()}" \
                  f"\nTemperatura: {message_dict['main']['temp']}°{temp_unit}" \
                  f"\nPercepita: {message_dict['main']['feels_like']}°{temp_unit}" \
                  f"\nUmidità: {message_dict['main']['humidity']}%"
        query.edit_message_text(text=message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    except KeyError:
        query.edit_message_text(text="Località non ancora specificata", reply_markup=reply_markup)


def forecast(update: Update, context: CallbackContext):
    global curr_forecast_index
    global messages

    query = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton("◀", callback_data="back:from_forecast"),
                 InlineKeyboardButton("▶", callback_data="next")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        data: dict = context.user_data
        lat = data["location_lat"]
        lon = data["location_lon"]
        unit = data.get("measure_unit", "metric")
        name = data["name"]
        temp_unit = "F" if unit == "imperial" else "C"
        vel_unit = "mph" if unit == "imperial" else "km/h"

        if len(messages) == 0:
            messages = openweather.get_daily_forecast(lat, lon, unit)

    except KeyError:
        keyboard[0].pop(1)
        query.edit_message_text(text="Località non ancora specificata", reply_markup=reply_markup)
        return

    if curr_forecast_index >= len(messages) - 1:
        keyboard[0].pop(1)

    if curr_forecast_index < 0:
        curr_forecast_index += 1
        print("curr_index: ", curr_forecast_index)
        return
    elif curr_forecast_index >= len(messages):
        curr_forecast_index -= 1

        print("curr_index: ", curr_forecast_index)
        return
    else:
        message = messages[curr_forecast_index]

    wind = message["wind_speed"] if unit == "imperial" else message["wind_speed"] * 3.6
    pretty_message = f"*{name.upper()}\n" \
                     f"*{datetime.utcfromtimestamp(message['dt']).strftime('%d/%m/%Y')}\n\n" \
                     f"🌄 *Alba*: {datetime.utcfromtimestamp(message['sunrise']).strftime('%H:%M')}\n" \
                     f"🌇 *Tramonto*: {datetime.utcfromtimestamp(message['sunset']).strftime('%H:%M')}\n" \
                     f"🌡 *Temperatura*:\n" \
                     f"         *Min*: {message['temp']['min']}°{temp_unit}\n" \
                     f"         *Max*: {message['temp']['max']}°{temp_unit}\n" \
                     f"🍃 *Vento*: {round(wind, 3)}{vel_unit}\n" \
                     f"⏱ *Pressione*: {message['pressure']}hPa\n" \
                     f"💧 *Umidità*: {message['humidity']}%\n"
    query.delete_message()
    context.bot.send_message(chat_id=update.effective_chat.id, text=pretty_message,
                             parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    # pprint(messages)


def next_day(update: Update, context: CallbackContext):
    global curr_forecast_index
    curr_forecast_index += 1
    forecast(update, context)


def preferences(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [[
        InlineKeyboardButton("🗺 Località", callback_data='location'),
        InlineKeyboardButton("🌡 Unità di misura", callback_data='unit_select')],
        [InlineKeyboardButton("◀", callback_data="back:to_start")]]
    query.edit_message_text(text="Modifica le impostazioni",
                            reply_markup=InlineKeyboardMarkup(keyboard))


def present_measure_unit(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [[
        InlineKeyboardButton("Metrico", callback_data='unit:metric'),
        InlineKeyboardButton("Imperiale", callback_data='unit:imperial')],
        [InlineKeyboardButton("◀", callback_data="back:to_preferences")]]

    query.edit_message_text(text="Seleziona il sistema di unità di misura che preferisci",
                            reply_markup=InlineKeyboardMarkup(keyboard))


def select_measure_unit(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    unit = update.callback_query.data[5:]
    context.user_data["measure_unit"] = unit
    query.edit_message_text(text="Opzione aggiornata")
    start(update, context)


def ask_for_location(update: Update, context: CallbackContext):
    # Starting point
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("◀", callback_data="back_to_preferences")]]
    query.edit_message_text(text="Di quale città vuoi sapere il meteo?",
                            reply_markup=InlineKeyboardMarkup(keyboard))
    return 0


def present_locations(update: Update, context: CallbackContext):
    message = update.message.text
    results = openweather.search_location(message)
    keyboard = [InlineKeyboardButton(f"{i['name']}, {i['country']}",
                                     callback_data=f"loc:{i['name']}|{i['lat']}:{i['lon']}") for i in results]
    keyboard = [[i] for i in keyboard]
    keyboard.append([InlineKeyboardButton("◀", callback_data="back_to_preferences")])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Seleziona la città",
                             reply_markup=InlineKeyboardMarkup(keyboard))
    return 1


def location_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = update.callback_query.data
    name = data[4:data.rindex("|")]
    lat = data[data.rindex("|") + 1:data.rindex(":")]
    lon = data[data.rindex(":") + 1:]
    context.user_data["location_lat"] = lat
    context.user_data["location_lon"] = lon
    context.user_data["name"] = name
    query.edit_message_text(text="Città selezionata")

    start(update, context)

    return ConversationHandler.END


def back(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    data = data[data.index(":") + 1:]

    if data == "to_start":
        query.delete_message()
        start(update, context)

    elif data == "to_preferences":
        return back_to_pref(update, context)

    elif data == "from_forecast":
        global curr_forecast_index
        if curr_forecast_index == 0:
            query.delete_message()
            start(update, context)
        else:
            curr_forecast_index -= 1
            forecast(update, context)


def back_to_pref(update: Update, context: CallbackContext):
    preferences(update, context)
    return ConversationHandler.END


def error(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Si è verificato un errore, si prega di provare di nuovo")
    print(context.error)
    start(update, context)
    context.bot.delete_message(update.message.message_id)
    return -1
