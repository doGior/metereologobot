import requests
import json


class OpenWeather:
    def __init__(self):
        self.baseurl = "http://api.openweathermap.org/"
        self.appid = "<TOKEN>"

    def search_location(self, city: str) -> list[dict]:
        """
        Returns locations found
        :param city: city name or postal code
        :return: list of locations (json)
        """
        url = self.baseurl + "/geo/1.0/direct"
        response = requests.get(url, params={'q': city, "appid": self.appid})
        return json.loads(response.text)

    def get_current_conditions(self, latitude: str, longitude: str, unit: str) -> dict:
        """
        Returns current conditions in your specified location
        :param latitude: value obtained by OpenWeather.search_location() method
        :param longitude: value obtained by OpenWeather.search_location() method
        :param unit: unit of measurement (metric/imperial)
        :return: current condition information as a json
        """
        url = self.baseurl + "/data/2.5/weather"
        response = requests.get(url, params={"appid": self.appid, "lat": latitude, "lon": longitude,
                                             "lang": "it", "units": unit})
        return json.loads(response.text)

    def get_daily_forecast(self, latitude: str, longitude: str, unit: str) -> list[dict]:
        """
        Return the forecast for the next amount of days you specified
        :param location_key: key obtained with the get_location_key() method
        :param days: number of days to get the forecast, IT HAS TO BE 1, 5
        :return: forecast informations
        """
        url = self.baseurl + f"/data/2.5/onecall"
        response = requests.get(url, params={"appid": self.appid, "lat": latitude, "lon": longitude, "units": unit,
                                             "lang": "it", "exclude": "current,minutely,hourly,alerts"})
        return json.loads(response.text)['daily']
