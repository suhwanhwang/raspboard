import tkinter as tk
from datetime import datetime
from .config.settings import Settings
from .api.openweather_api import OpenWeatherAPI
from .ui.weather_widgets import WeatherWidgets
from .models.weather_data import WeatherData

class WeatherFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.setup_environment()
        self.setup_window()
        self.create_widgets()
        self.start_updates()

    def setup_environment(self):
        self.settings = Settings()
        self.weather_api = OpenWeatherAPI(self.settings.api_key, self.settings.language)

    def setup_window(self):
        self.title("Weather Frame")
        self.attributes('-fullscreen', True)
        self.configure(bg='black')
        self.main_frame = tk.Frame(self, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        self.bind('<Escape>', lambda e: self.quit())

    def create_widgets(self):
        self.weather_widgets = WeatherWidgets(self.main_frame, self.settings.language)

    def start_updates(self):
        self.update_weather()
        self.update_time()
        self.after(300000, self.update_weather)  # Update weather every 5 minutes
        self.after(1000, self.update_time)  # Update time every second

    def update_time(self):
        self.weather_widgets.update_time(datetime.now())
        self.after(1000, self.update_time)

    def update_weather(self):
        try:
            current_data = self.weather_api.get_current_weather(self.settings.city)
            air_data = self.weather_api.get_air_quality(
                current_data['coord']['lat'],
                current_data['coord']['lon']
            )
            forecast_data = self.weather_api.get_forecast(self.settings.city)

            weather_data = WeatherData.from_api_response(current_data, air_data, forecast_data)
            self.weather_widgets.update_weather(weather_data)

        except Exception as e:
            print(f"Error updating weather: {str(e)}")
            print(f"Full error details: {type(e).__name__}")

        self.after(300000, self.update_weather)  # Update every 5 minutes

def main():
    app = WeatherFrame()
    app.mainloop()

if __name__ == "__main__":
    main() 