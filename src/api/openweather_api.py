import requests
from typing import Dict, Any
from .weather_api import WeatherAPI

class OpenWeatherAPI(WeatherAPI):
    def __init__(self, api_key: str, language: str = 'en'):
        self.api_key = api_key
        self.language = language
        self.base_url = "https://api.openweathermap.org/data/2.5"
        # Reuse a single HTTP session for connection pooling and lower latency
        self.session = requests.Session()
        # Default timeouts: (connect_timeout, read_timeout)
        self._timeout = (3, 5)

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        params = {'q': city, 'appid': self.api_key, 'units': 'metric', 'lang': self.language}
        response = self.session.get(f"{self.base_url}/weather", params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        params = {'lat': lat, 'lon': lon, 'appid': self.api_key}
        response = self.session.get(f"{self.base_url}/air_pollution", params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, city: str) -> Dict[str, Any]:
        params = {'q': city, 'appid': self.api_key, 'units': 'metric', 'lang': self.language}
        response = self.session.get(f"{self.base_url}/forecast", params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_weather_icon_url(self, icon_code: str, size: str = '2x') -> str:
        return f"https://openweathermap.org/img/wn/{icon_code}@{size}.png" 