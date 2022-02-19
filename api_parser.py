import requests
import json


class OpenWeather:
    def __init__(self):
        self.urlbase = "http://api.openweathermap.org/"
        self.appid = "<TOKEN>"

    def cerca_luogo(self, citta: str) -> list[dict]:
        """
        Restituisce un elenco di luoghi trovati interrogando l'API
        :param citta: Nome della città
        :return: Lista di luoghi (JSON)
        """
        endpoint = "/geo/1.0/direct"
        url = self.urlbase + endpoint
        risposta = requests.get(url, params={'q': citta, "appid": self.appid})
        return json.loads(risposta.text)

    def get_condizioni_attuali(self, latitudine: str, longitudine: str, unita_misura: str) -> dict:
        """
        Restituisce le informazioni relative alle
        condizioni meteo attuali nelle coordinate specificate

        :param latitudine: Coordinata ottenuta dal metodo OpenWeather.cerca_luogo()
        :param longitudine: Coordinata ottenuta dal metodo OpenWeather.cerca_luogo()
        :param unita_misura: Unità di misura (metric/imperial)
        :return: Informazioni in formato JSON
        """
        endpoint = "/data/2.5/weather"
        url = self.urlbase + endpoint
        risposta = requests.get(url, params={"appid": self.appid, "lat": latitudine, "lon": longitudine,
                                             "lang": "it", "units": unita_misura})
        return json.loads(risposta.text)

    def get_previsioni(self, latitudine: str, longitudine: str, unita_misura: str) -> list[dict]:
        """
        Restituisce le informazioni relative alle previsioni
        meteo dei prossimi giorni nelle coordinate specificate
        :param latitudine: Coordinata ottenuta dal metodo OpenWeather.cerca_luogo()
        :param longitudine: Coordinata ottenuta dal metodo OpenWeather.cerca_luogo()
        :param unita_misura: Unità di misura (metric/imperial)
        :return: Informazioni in formato JSON
        """
        endpoint = "/data/2.5/onecall"
        url = self.urlbase + endpoint
        risposta = requests.get(url, params={"appid": self.appid, "lat": latitudine,
                                             "lon": longitudine, "units": unita_misura,
                                             "lang": "it", "exclude": "current,minutely,hourly,alerts"})
        return json.loads(risposta.text)['daily']
