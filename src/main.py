import tkinter as tk
from datetime import datetime
import psutil
import gc
import time
import logging
import requests
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
                # Calculate wait time based on consecutive errors (exponential backoff)
                # Wait 5 mins * 2^(errors-1), up to a max of ~1 hour (12 * 5 mins)
                wait_factor = 2**(min(self.consecutive_errors, 5) - 1) # Limit exponent to avoid excessive wait
                wait_time_seconds = 300 * wait_factor 
                # Check if enough time has passed since the last attempt
                if time.time() - self.last_successful_update < wait_time_seconds:
                    logging.info(f"Waiting {wait_time_seconds} seconds before retry due to {self.consecutive_errors} previous errors.")
                    # No need to schedule again here, finally block will do it
                    return
                else:
                     logging.info(f"Attempting update after waiting period. Consecutive errors: {self.consecutive_errors}")

            current_data = self.weather_api.get_current_weather(self.settings.city)
            air_data = self.weather_api.get_air_quality(
                current_data['coord']['lat'],
                current_data['coord']['lon']
            )
            forecast_data = self.weather_api.get_forecast(self.settings.city)

            weather_data = WeatherData.from_api_response(current_data, air_data, forecast_data)
            self.weather_widgets.update_weather(weather_data)

            # Reset error counter on success
            if self.consecutive_errors > 0:
                logging.info(f"Weather update successful after {self.consecutive_errors} failures.")
            else:
                 logging.info("Weather update successful")
            self.consecutive_errors = 0
            self.last_successful_update = time.time() # Record time of last successful update

        except requests.exceptions.RequestException as req_err:
            self.consecutive_errors += 1
            error_type = type(req_err).__name__
            error_msg = str(req_err)
            log_level = logging.WARNING # Default level for request errors
            if "NameResolutionError" in error_msg:
                log_level = logging.ERROR # Elevate log level for DNS issues
                logging.error("DNS Resolution failed for api.openweathermap.org. Check network/DNS settings.")
            else:
                 logging.warning(f"API Request failed: {error_msg}")

            logging.log(log_level, f"Error updating weather: {error_msg}")
            logging.log(log_level, f"Full error details: {error_type}")
            logging.log(log_level, f"Consecutive errors: {self.consecutive_errors}")
            # last_successful_update remains unchanged on error

        except Exception as e:
            self.consecutive_errors += 1
            logging.error(f"Unexpected error during weather update: {str(e)}", exc_info=True)
            logging.error(f"Full error details: {type(e).__name__}")
            logging.error(f"Consecutive errors: {self.consecutive_errors}")
            # last_successful_update remains unchanged on error

        finally:
            # Always schedule the next update check
            self.after(300000, self.update_weather) # Schedule next check in 5 minutes

def main():
    try:
        app = WeatherFrame()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Critical error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    main() 