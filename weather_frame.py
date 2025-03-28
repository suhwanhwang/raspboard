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

        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.city = os.getenv('CITY', 'Seoul')  # Default city is Seoul
        self.language = os.getenv('LANGUAGE', 'kr')  # Default language is Korean

        if not self.api_key:
            print("Error: OpenWeather API key not found in .env file!")
            self.quit()
            return

        # Configure window
        self.title("Weather Frame")
        self.attributes('-fullscreen', True)
        self.configure(bg='black')

        # Create main frame
        self.main_frame = tk.Frame(self, bg='black')
        self.main_frame.pack(expand=True, fill='both')

        # Create widgets
        self.create_widgets()
        
        # Update weather initially and schedule updates
        self.update_weather()
        self.update_time()
        
        # Schedule updates
        self.after(300000, self.update_weather)  # Update weather every 5 minutes
        self.after(1000, self.update_time)  # Update time every second

        # Bind escape key to close
        self.bind('<Escape>', lambda e: self.quit())

    def create_widgets(self):
        # Time label
        self.time_label = tk.Label(
            self.main_frame,
            font=('Helvetica', 96),
            foreground='white',
            bg='black'
        )
        self.time_label.pack(pady=20)

        # Date label
        self.date_label = tk.Label(
            self.main_frame,
            font=('Helvetica', 48),
            foreground='white',
            bg='black'
        )
        self.date_label.pack(pady=10)

        # Current weather frame
        current_weather_frame = tk.Frame(self.main_frame, bg='black')
        current_weather_frame.pack(pady=20)

        # Temperature label
        self.temp_label = tk.Label(
            current_weather_frame,
            font=('Helvetica', 120),
            foreground='white',
            bg='black'
        )
        self.temp_label.pack(side='left', padx=20)

        # Min/Max temperature frame
        minmax_frame = tk.Frame(current_weather_frame, bg='black')
        minmax_frame.pack(side='left', padx=20)

        self.temp_min_label = tk.Label(
            minmax_frame,
            font=('Helvetica', 36),
            foreground='#4a90e2',  # Blue color for min temp
            bg='black'
        )
        self.temp_min_label.pack()

        self.temp_max_label = tk.Label(
            minmax_frame,
            font=('Helvetica', 36),
            foreground='#e24a4a',  # Red color for max temp
            bg='black'
        )
        self.temp_max_label.pack()

        # Weather icon label
        self.icon_label = tk.Label(
            current_weather_frame,
            bg='black'
        )
        self.icon_label.pack(side='left', padx=20)

        # Weather description label
        self.desc_label = tk.Label(
            self.main_frame,
            font=('Helvetica', 48),
            foreground='white',
            bg='black'
        )
        self.desc_label.pack(pady=10)

        # Weekly forecast frame
        self.forecast_frame = tk.Frame(self.main_frame, bg='black')
        self.forecast_frame.pack(side='bottom', fill='x', pady=20)

        # Create a container frame for centering
        forecast_container = tk.Frame(self.forecast_frame, bg='black')
        forecast_container.pack(expand=True)
        
        # Create 7 day forecast widgets
        self.forecast_widgets = []
        for i in range(7):
            day_frame = tk.Frame(forecast_container, bg='black')
            day_frame.pack(side='left', padx=10)  # Reduced padding
            
            day_label = tk.Label(
                day_frame,
                font=('Helvetica', 20),  # Reduced font size
                foreground='white',
                bg='black'
            )
            day_label.pack()
            
            icon_label = tk.Label(
                day_frame,
                bg='black'
            )
            icon_label.pack(pady=2)  # Reduced padding
            
            temp_label = tk.Label(
                day_frame,
                font=('Helvetica', 20),  # Reduced font size
                foreground='white',
                bg='black'
            )
            temp_label.pack()
            
            self.forecast_widgets.append({
                'day': day_label,
                'icon': icon_label,
                'temp': temp_label
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

    def update_weather(self):
        try:
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric&lang={self.language}"
            current_response = requests.get(current_url)
            
            if current_response.status_code != 200:
                print(f"Error: API request failed with status code {current_response.status_code}")
                print(f"Response: {current_response.text}")
                return
                
            current_data = current_response.json()
            
            if 'main' not in current_data:
                print(f"Error: Invalid API response format. Response: {current_data}")
                return

            # Update current weather
            temp = round(current_data['main']['temp'])
            temp_min = round(current_data['main']['temp_min'])
            temp_max = round(current_data['main']['temp_max'])
            
            self.temp_label.config(text=f"{temp}°C")
            self.temp_min_label.config(text=f"↓{temp_min}°C")
            self.temp_max_label.config(text=f"↑{temp_max}°C")

            if 'weather' not in current_data or not current_data['weather']:
                print("Error: Weather data not found in API response")
                return

            desc = current_data['weather'][0]['description']
            self.desc_label.config(text=desc)

            icon_code = current_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"  # Using larger icons
            
            icon_response = requests.get(icon_url)
            if icon_response.status_code != 200:
                print(f"Error: Failed to fetch weather icon. Status code: {icon_response.status_code}")
                return
                
            icon_image = Image.open(io.BytesIO(icon_response.content))
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            self.icon_label.config(image=icon_photo)
            self.icon_label.image = icon_photo

            # Weekly forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=metric&lang={self.language}"
            forecast_response = requests.get(forecast_url)
            
            if forecast_response.status_code != 200:
                print(f"Error: Forecast API request failed with status code {forecast_response.status_code}")
                print(f"Response: {forecast_response.text}")
                return
                
            forecast_data = forecast_response.json()
            
            if 'list' not in forecast_data:
                print(f"Error: Invalid forecast API response format. Response: {forecast_data}")
                return

            # Process forecast data (get one forecast per day)
            daily_forecasts = {}
            for item in forecast_data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_forecasts and len(daily_forecasts) < 7:
                    daily_forecasts[date] = item

            # Update forecast widgets
            if self.language == 'kr':
                weekday_names = ['월', '화', '수', '목', '금', '토', '일']
            else:
                weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

            for i, (date, day_data) in enumerate(list(daily_forecasts.items())[:7]):
                day_name = weekday_names[date.weekday()]
                temp = round(day_data['main']['temp'])
                icon_code = day_data['weather'][0]['icon']

                self.forecast_widgets[i]['day'].config(text=day_name)
                self.forecast_widgets[i]['temp'].config(text=f"{temp}°C")

                # Update icon
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                icon_response = requests.get(icon_url)
                if icon_response.status_code != 200:
                    print(f"Error: Failed to fetch forecast icon. Status code: {icon_response.status_code}")
                    continue
                    
                icon_image = Image.open(io.BytesIO(icon_response.content))
                icon_photo = ImageTk.PhotoImage(icon_image)
                
                self.forecast_widgets[i]['icon'].config(image=icon_photo)
                self.forecast_widgets[i]['icon'].image = icon_photo  # Keep a reference

        except Exception as e:
            print(f"Error updating weather: {str(e)}")
            print(f"Full error details: {type(e).__name__}")

        self.after(300000, self.update_weather)  # Update every 5 minutes

if __name__ == "__main__":
    app = WeatherFrame()
    app.mainloop()