from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, date

@dataclass
class WeatherCondition:
    description: str
    icon: str

@dataclass
class CurrentWeather:
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    weather: WeatherCondition
    air_quality: int
    rain_amount: float  # 1시간 동안의 강수량 (mm)
    snow_amount: float  # 1시간 동안의 적설량 (mm)

@dataclass
class DailyForecast:
    date: date
    temp_min: float
    temp_max: float

@dataclass
class WeatherData:
    current: CurrentWeather
    forecast: List[DailyForecast]

    @classmethod
    def from_api_response(cls, current_data: Dict[str, Any], air_data: Dict[str, Any], forecast_data: Dict[str, Any]) -> 'WeatherData':
        # Get rain and snow amounts
        rain_amount = current_data.get('rain', {}).get('1h', 0)
        snow_amount = current_data.get('snow', {}).get('1h', 0)

        current = CurrentWeather(
            temperature=current_data['main']['temp'],
            feels_like=current_data['main']['feels_like'],
            humidity=current_data['main']['humidity'],
            wind_speed=current_data['wind']['speed'],
            weather=WeatherCondition(
                description=current_data['weather'][0]['description'],
                icon=current_data['weather'][0]['icon']
            ),
            air_quality=air_data['list'][0]['main']['aqi'] if air_data and 'list' in air_data and air_data['list'] else 0,
            rain_amount=rain_amount,
            snow_amount=snow_amount
        )

        # Aggregate the 3-hour forecast slots into a daily min/max range.
        daily_forecasts: Dict[date, DailyForecast] = {}
        for item in forecast_data['list']:
            day = datetime.fromtimestamp(item['dt']).date()
            temp_min = item['main']['temp_min']
            temp_max = item['main']['temp_max']
            if day not in daily_forecasts:
                daily_forecasts[day] = DailyForecast(date=day, temp_min=temp_min, temp_max=temp_max)
            else:
                forecast = daily_forecasts[day]
                forecast.temp_min = min(forecast.temp_min, temp_min)
                forecast.temp_max = max(forecast.temp_max, temp_max)
        return cls(
            current=current,
            forecast=list(daily_forecasts.values())[:5]  # Get only 5 days of forecast
        ) 