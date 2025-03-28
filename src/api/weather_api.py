from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class WeatherAPI(ABC):
    @abstractmethod
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather data for a city."""
        pass

    @abstractmethod
    def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get air quality data for given coordinates."""
        pass

    @abstractmethod
    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get weather forecast data for a city."""
        pass

    @abstractmethod
    def get_weather_icon_url(self, icon_code: str, size: str = '2x') -> str:
        """Get URL for weather icon."""
        pass 