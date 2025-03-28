import tkinter as tk
from datetime import datetime
import requests
from PIL import Image, ImageTk
import io
import os
from dotenv import load_dotenv

class WeatherFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.setup_environment()
        self.setup_window()
        self.create_widgets()
        self.start_updates()

    def setup_environment(self):
        load_dotenv()
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.city = os.getenv('CITY', 'Seoul')
        self.language = os.getenv('LANGUAGE', 'kr')

        if not self.api_key:
            print("Error: OpenWeather API key not found in .env file!")
            self.quit()
            return

    def setup_window(self):
        self.title("Weather Frame")
        self.attributes('-fullscreen', True)
        self.configure(bg='black')
        self.main_frame = tk.Frame(self, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        self.bind('<Escape>', lambda e: self.quit())

    def start_updates(self):
        self.update_weather()
        self.update_time()
        self.after(300000, self.update_weather)  # Update weather every 5 minutes
        self.after(1000, self.update_time)  # Update time every second

    def create_widgets(self):
        # Create main container frame for centering
        self.container_frame = tk.Frame(self.main_frame, bg='black')
        self.container_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.create_time_widgets()
        self.create_weather_widgets()

    def create_time_widgets(self):
        # Date label
        self.date_label = tk.Label(
            self.container_frame,
            font=('Helvetica', 48),
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
            font=('Helvetica', 36),
            foreground='white',
            bg='black'
        )
        self.air_quality_label.pack(pady=10)

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

    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        
        if self.language == 'kr':
            weekday_names = ['월', '화', '수', '목', '금', '토', '일']
            date_str = now.strftime("%Y년 %m월 %d일 ") + weekday_names[now.weekday()]
        else:
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            date_str = now.strftime("%B %d, %Y ") + weekday_names[now.weekday()]
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        self.after(1000, self.update_time)

    def fetch_weather_data(self):
        try:
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric&lang={self.language}"
            current_response = requests.get(current_url)
            
            if current_response.status_code != 200:
                print(f"Error: API request failed with status code {current_response.status_code}")
                print(f"Response: {current_response.text}")
                return None
                
            current_data = current_response.json()
            
            if 'main' not in current_data or 'weather' not in current_data or not current_data['weather']:
                print("Error: Invalid API response format")
                return None

            # Get air quality data
            air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={current_data['coord']['lat']}&lon={current_data['coord']['lon']}&appid={self.api_key}"
            air_response = requests.get(air_url)
            air_data = air_response.json() if air_response.status_code == 200 else None

            # Get forecast data
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=metric&lang={self.language}"
            forecast_response = requests.get(forecast_url)
            
            if forecast_response.status_code != 200:
                print(f"Error: Forecast API request failed with status code {forecast_response.status_code}")
                return None
                
            forecast_data = forecast_response.json()
            
            if 'list' not in forecast_data:
                print("Error: Invalid forecast API response format")
                return None

            return {
                'current': current_data,
                'air': air_data,
                'forecast': forecast_data
            }

        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None

    def process_forecast_data(self, forecast_data):
        daily_forecasts = {}
        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'temp': item['main']['temp'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'weather': item['weather'][0],
                    'dt': item['dt']
                }
            else:
                # Update min/max temperatures
                daily_forecasts[date]['temp_min'] = min(daily_forecasts[date]['temp_min'], item['main']['temp_min'])
                daily_forecasts[date]['temp_max'] = max(daily_forecasts[date]['temp_max'], item['main']['temp_max'])
                # Update weather if it's during daytime (between 9 AM and 6 PM)
                hour = datetime.fromtimestamp(item['dt']).hour
                if 9 <= hour <= 18:
                    daily_forecasts[date]['weather'] = item['weather'][0]
                    daily_forecasts[date]['temp'] = item['main']['temp']
                    daily_forecasts[date]['dt'] = item['dt']
        return daily_forecasts

    def update_weather(self):
        try:
            weather_data = self.fetch_weather_data()
            if not weather_data:
                return

            current_data = weather_data['current']
            air_data = weather_data['air']
            forecast_data = weather_data['forecast']

            # Update current weather
            temp = round(current_data['main']['temp'])
            self.temp_label.config(text=f"{temp}°C")

            # Update weather description and icon
            desc = current_data['weather'][0]['description']
            self.desc_label.config(text=desc)

            icon_code = current_data['weather'][0]['icon']
            self.update_weather_icon(icon_code, self.icon_label, size='4x')

            # Update air quality
            if air_data and 'list' in air_data and air_data['list']:
                aqi = air_data['list'][0]['main']['aqi']
                aqi_text = self.get_air_quality_text(aqi)
                aqi_color = self.get_air_quality_color(aqi)
                
                if self.language == 'kr':
                    self.air_quality_label.config(
                        text=f"대기질: {aqi_text}",
                        foreground=aqi_color
                    )
                else:
                    self.air_quality_label.config(
                        text=f"Air Quality: {aqi_text}",
                        foreground=aqi_color
                    )

            # Update forecast
            daily_forecasts = self.process_forecast_data(forecast_data)
            self.update_forecast_widgets(daily_forecasts)

        except Exception as e:
            print(f"Error updating weather: {str(e)}")
            print(f"Full error details: {type(e).__name__}")

        self.after(300000, self.update_weather)  # Update every 5 minutes

    def update_weather_icon(self, icon_code, label, size='2x'):
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@{size}.png"
        icon_response = requests.get(icon_url)
        if icon_response.status_code != 200:
            print(f"Error: Failed to fetch weather icon. Status code: {icon_response.status_code}")
            return
            
        icon_image = Image.open(io.BytesIO(icon_response.content))
        icon_photo = ImageTk.PhotoImage(icon_image)
        
        label.config(image=icon_photo)
        label.image = icon_photo  # Keep a reference

    def update_forecast_widgets(self, daily_forecasts):
        if self.language == 'kr':
            weekday_names = ['월', '화', '수', '목', '금', '토', '일']
        else:
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for i, (date, day_data) in enumerate(list(daily_forecasts.items())[:7]):
            day_name = weekday_names[date.weekday()]
            temp_min = round(day_data['temp_min'])
            temp_max = round(day_data['temp_max'])
            icon_code = day_data['weather']['icon']

            self.forecast_widgets[i]['day'].config(text=day_name)
            self.forecast_widgets[i]['temp_min'].config(text=f"↓{temp_min}°")
            self.forecast_widgets[i]['temp_max'].config(text=f"↑{temp_max}°")
            self.update_weather_icon(icon_code, self.forecast_widgets[i]['icon'])

    def get_air_quality_text(self, aqi):
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

    def get_air_quality_color(self, aqi):
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

if __name__ == "__main__":
    app = WeatherFrame()
    app.mainloop()