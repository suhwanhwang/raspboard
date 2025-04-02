import tkinter as tk
from datetime import datetime
import psutil
import gc
import time
import logging
from .config.settings import Settings
from .api.openweather_api import OpenWeatherAPI
from .ui.weather_widgets import WeatherWidgets
from .models.weather_data import WeatherData

# Configure logging
logging.basicConfig(
    filename='weather_frame.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WeatherFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.consecutive_errors = 0
        self.last_successful_update = time.time()
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
        # Hide mouse cursor
        self.config(cursor="none")

    def create_widgets(self):
        self.weather_widgets = WeatherWidgets(self.main_frame, self.settings.language)

    def log_system_stats(self):
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            logging.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
            logging.info(f"CPU usage: {process.cpu_percent()}%")
        except Exception as e:
            logging.error(f"Error logging system stats: {str(e)}")

    def start_updates(self):
        self.update_weather()
        self.update_time()
        self.after(300000, self.update_weather)  # Update weather every 5 minutes
        self.after(1000, self.update_time)  # Update time every second
        self.after(300000, self.log_system_stats)  # Log system stats every 5 minutes
        self.after(3600000, self.cleanup)  # Run cleanup every hour

    def update_time(self):
        self.weather_widgets.update_time(datetime.now())
        self.after(1000, self.update_time)

    def cleanup(self):
        gc.collect()  # Force garbage collection
        self.log_system_stats()
        self.after(3600000, self.cleanup)

    def update_weather(self):
        try:
            # If there were consecutive errors, wait before retrying
            if self.consecutive_errors > 0:
                wait_time = min(300 * self.consecutive_errors, 3600)  # Max 1 hour wait
                if time.time() - self.last_successful_update < wait_time:
                    logging.info(f"Waiting {wait_time} seconds before retry due to previous errors")
                    self.after(300000, self.update_weather)
                    return

            current_data = self.weather_api.get_current_weather(self.settings.city)
            air_data = self.weather_api.get_air_quality(
                current_data['coord']['lat'],
                current_data['coord']['lon']
            )
            forecast_data = self.weather_api.get_forecast(self.settings.city)

            weather_data = WeatherData.from_api_response(current_data, air_data, forecast_data)
            self.weather_widgets.update_weather(weather_data)
            
            # Reset error counter on success
            self.consecutive_errors = 0
            self.last_successful_update = time.time()
            logging.info("Weather update successful")

        except Exception as e:
            self.consecutive_errors += 1
            logging.error(f"Error updating weather: {str(e)}")
            logging.error(f"Full error details: {type(e).__name__}")
            logging.error(f"Consecutive errors: {self.consecutive_errors}")

        self.after(300000, self.update_weather)  # Update every 5 minutes

def main():
    try:
        app = WeatherFrame()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Critical error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    main() 