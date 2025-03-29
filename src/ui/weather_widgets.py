import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
from typing import List, Dict, Any
from ..models.weather_data import WeatherData

class WeatherWidgets:
    def __init__(self, parent: tk.Frame, language: str = 'en'):
        self.parent = parent
        self.language = language
        self.setup_widgets()

    def setup_widgets(self):
        # Create main container frame for centering
        self.container_frame = tk.Frame(self.parent, bg='black')
        self.container_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.create_time_widgets()
        self.create_weather_widgets()
        self.create_temperature_range_widgets()

    def create_time_widgets(self):
        # Date label
        self.date_label = tk.Label(
            self.container_frame,
            font=('Helvetica', 72),
            foreground='white',
            bg='black'
        )
        self.date_label.pack(pady=20)

        # Time label
        self.time_label = tk.Label(
            self.container_frame,
            font=('Helvetica', 96),
            foreground='white',
            bg='black'
        )
        self.time_label.pack(pady=20)

    def create_weather_widgets(self):
        # Current weather frame
        current_weather_frame = tk.Frame(self.container_frame, bg='black')
        current_weather_frame.pack(pady=20)

        # Temperature label
        self.temp_label = tk.Label(
            current_weather_frame,
            font=('Helvetica', 120),
            foreground='white',
            bg='black'
        )
        self.temp_label.pack(side='left', padx=20)

        # Weather icon label
        self.icon_label = tk.Label(
            current_weather_frame,
            bg='black'
        )
        self.icon_label.pack(side='left', padx=20)

        # Weather info frame
        weather_info_frame = tk.Frame(current_weather_frame, bg='black')
        weather_info_frame.pack(side='left', padx=20)

        # Weather description label
        self.desc_label = tk.Label(
            weather_info_frame,
            font=('Helvetica', 60),
            foreground='white',
            bg='black'
        )
        self.desc_label.pack(pady=10)

        # Air quality label
        self.air_quality_label = tk.Label(
            weather_info_frame,
            font=('Helvetica', 60),
            foreground='white',
            bg='black'
        )
        self.air_quality_label.pack(pady=10)

    def create_temperature_range_widgets(self):
        # Temperature range frame
        temp_range_frame = tk.Frame(self.container_frame, bg='black')
        temp_range_frame.pack(pady=20)

        # Min temperature label
        self.temp_min_label = tk.Label(
            temp_range_frame,
            font=('Helvetica', 96),
            foreground='#00bfff',  # Brighter blue
            bg='black'
        )
        self.temp_min_label.pack(side='left', padx=20)

        # Max temperature label
        self.temp_max_label = tk.Label(
            temp_range_frame,
            font=('Helvetica', 96),
            foreground='#ff4d4d',  # Brighter red
            bg='black'
        )
        self.temp_max_label.pack(side='left', padx=20)

        # Precipitation info frame
        precip_frame = tk.Frame(temp_range_frame, bg='black')
        precip_frame.pack(side='left', padx=20)

        # Rain amount label
        self.rain_label = tk.Label(
            precip_frame,
            font=('Helvetica', 72),
            foreground='#4a90e2',
            bg='black'
        )
        self.rain_label.pack(side='left', padx=10)

        # Snow amount label
        self.snow_label = tk.Label(
            precip_frame,
            font=('Helvetica', 72),
            foreground='#ffffff',
            bg='black'
        )
        self.snow_label.pack(side='left', padx=10)

    def update_time(self, now):
        time_str = now.strftime("%I:%M %p")
        
        if self.language == 'kr':
            weekday_names = ['월', '화', '수', '목', '금', '토', '일']
            date_str = now.strftime("%Y년 %m월 %d일 ") + weekday_names[now.weekday()]
        else:
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            date_str = now.strftime("%B %d, %Y ") + weekday_names[now.weekday()]
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)

    def update_weather(self, weather_data: WeatherData):
        # Update current weather
        self.temp_label.config(text=f"{round(weather_data.current.temperature)}°C")
        self.desc_label.config(text=weather_data.current.weather.description)
        self.update_weather_icon(weather_data.current.weather.icon, self.icon_label, size='4x')

        # Update air quality
        aqi_text = self.get_air_quality_text(weather_data.current.air_quality)
        
        if self.language == 'kr':
            self.air_quality_label.config(
                text=f"대기질: {aqi_text}"
            )
            # Update precipitation amounts
            if weather_data.current.rain_amount > 0:
                rain_intensity = self.get_rain_intensity_text(weather_data.current.rain_amount)
                self.rain_label.config(text=f"🌧️ {rain_intensity}")
            else:
                self.rain_label.config(text="")
            
            if weather_data.current.snow_amount > 0:
                snow_intensity = self.get_snow_intensity_text(weather_data.current.snow_amount)
                self.snow_label.config(text=f"🌨️ {snow_intensity}")
            else:
                self.snow_label.config(text="")
        else:
            self.air_quality_label.config(
                text=f"Air Quality: {aqi_text}"
            )
            # Update precipitation amounts
            if weather_data.current.rain_amount > 0:
                rain_intensity = self.get_rain_intensity_text(weather_data.current.rain_amount)
                self.rain_label.config(text=f"🌧️ {rain_intensity}")
            else:
                self.rain_label.config(text="")
            
            if weather_data.current.snow_amount > 0:
                snow_intensity = self.get_snow_intensity_text(weather_data.current.snow_amount)
                self.snow_label.config(text=f"🌨️ {snow_intensity}")
            else:
                self.snow_label.config(text="")

        # Update temperature range for the first day of forecast
        if weather_data.forecast and len(weather_data.forecast) > 0:
            first_day = weather_data.forecast[0]
            self.temp_min_label.config(text=f"↓{round(first_day.temp_min)}°")
            self.temp_max_label.config(text=f"↑{round(first_day.temp_max)}°")

    def update_weather_icon(self, icon_code: str, label: tk.Label, size: str = '2x'):
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@{size}.png"
        icon_response = requests.get(icon_url)
        if icon_response.status_code != 200:
            print(f"Error: Failed to fetch weather icon. Status code: {icon_response.status_code}")
            return
            
        icon_image = Image.open(io.BytesIO(icon_response.content))
        icon_photo = ImageTk.PhotoImage(icon_image)
        
        label.config(image=icon_photo)
        label.image = icon_photo  # Keep a reference

    def get_air_quality_text(self, aqi: int) -> str:
        if self.language == 'kr':
            if aqi == 1:
                return "좋음"
            elif aqi == 2:
                return "보통"
            elif aqi == 3:
                return "나쁨"
            elif aqi == 4:
                return "매우 나쁨"
            else:
                return "위험"
        else:
            if aqi == 1:
                return "Good"
            elif aqi == 2:
                return "Fair"
            elif aqi == 3:
                return "Poor"
            elif aqi == 4:
                return "Very Poor"
            else:
                return "Hazardous"

    def get_air_quality_color(self, aqi: int) -> str:
        if aqi == 1:
            return '#4CAF50'  # Green
        elif aqi == 2:
            return '#FFC107'  # Yellow
        elif aqi == 3:
            return '#FF9800'  # Orange
        elif aqi == 4:
            return '#F44336'  # Red
        else:
            return '#9C27B0'  # Purple

    def get_rain_intensity_text(self, rain_amount: float) -> str:
        if self.language == 'kr':
            if rain_amount < 0.1:
                return "가랑비"
            elif rain_amount < 2:
                return "약한비"
            elif rain_amount < 10:
                return "보통비"
            else:
                return "굵은비"
        else:
            if rain_amount < 0.1:
                return "Drizzle"
            elif rain_amount < 2:
                return "Light Rain"
            elif rain_amount < 10:
                return "Moderate Rain"
            else:
                return "Heavy Rain"

    def get_snow_intensity_text(self, snow_amount: float) -> str:
        if self.language == 'kr':
            if snow_amount < 0.1:
                return "가벼운눈"
            elif snow_amount < 2:
                return "약한눈"
            else:
                return "굵은눈"
        else:
            if snow_amount < 0.1:
                return "Light Snow"
            elif snow_amount < 2:
                return "Moderate Snow"
            else:
                return "Heavy Snow" 