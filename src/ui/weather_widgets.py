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
        self.create_forecast_widgets()

    def create_time_widgets(self):
        # Date label
        self.date_label = tk.Label(
            self.container_frame,
            font=('Helvetica', 60),
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
            font=('Helvetica', 48),
            foreground='white',
            bg='black'
        )
        self.desc_label.pack(pady=10)

        # Air quality label
        self.air_quality_label = tk.Label(
            weather_info_frame,
            font=('Helvetica', 48),
            foreground='white',
            bg='black'
        )
        self.air_quality_label.pack(pady=10)

    def create_forecast_widgets(self):
        # Weekly forecast frame
        self.forecast_frame = tk.Frame(self.container_frame, bg='black')
        self.forecast_frame.pack(pady=20)

        # Create a container frame for centering
        forecast_container = tk.Frame(self.forecast_frame, bg='black')
        forecast_container.pack(expand=True)
        
        # Create 5 day forecast widgets
        self.forecast_widgets = []
        for i in range(5):
            day_frame = tk.Frame(forecast_container, bg='black')
            day_frame.pack(side='left', padx=10)
            
            day_label = tk.Label(
                day_frame,
                font=('Helvetica', 20),
                foreground='white',
                bg='black'
            )
            day_label.pack()
            
            icon_label = tk.Label(
                day_frame,
                bg='black'
            )
            icon_label.pack(pady=2)
            
            minmax_frame = tk.Frame(day_frame, bg='black')
            minmax_frame.pack()
            
            temp_min_label = tk.Label(
                minmax_frame,
                font=('Helvetica', 20),
                foreground='#4a90e2',
                bg='black'
            )
            temp_min_label.pack(side='left', padx=2)
            
            temp_max_label = tk.Label(
                minmax_frame,
                font=('Helvetica', 20),
                foreground='#e24a4a',
                bg='black'
            )
            temp_max_label.pack(side='left', padx=2)
            
            self.forecast_widgets.append({
                'day': day_label,
                'icon': icon_label,
                'temp_min': temp_min_label,
                'temp_max': temp_max_label
            })

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
        else:
            self.air_quality_label.config(
                text=f"Air Quality: {aqi_text}"
            )

        # Update forecast
        self.update_forecast_widgets(weather_data.forecast)

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

    def update_forecast_widgets(self, forecast_data: List[Any]):
        if self.language == 'kr':
            weekday_names = ['월', '화', '수', '목', '금', '토', '일']
        else:
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for i, day_data in enumerate(forecast_data[:5]):
            day_name = weekday_names[day_data.date.weekday()]
            temp_min = round(day_data.temp_min)
            temp_max = round(day_data.temp_max)
            icon_code = day_data.weather.icon

            self.forecast_widgets[i]['day'].config(text=day_name)
            self.forecast_widgets[i]['temp_min'].config(text=f"↓{temp_min}°")
            self.forecast_widgets[i]['temp_max'].config(text=f"↑{temp_max}°")
            self.update_weather_icon(icon_code, self.forecast_widgets[i]['icon'])

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