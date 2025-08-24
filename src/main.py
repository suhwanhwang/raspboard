import tkinter as tk
from datetime import datetime
import psutil
import gc
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional, Callable
from queue import Queue, Empty
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
        self.is_fetching_weather: bool = False
        self.executor: Optional[ThreadPoolExecutor] = None
        self.ui_queue: Queue[Callable[[], None]] = Queue()
        self.setup_environment()
        self.setup_window()
        self.create_widgets()
        self.start_updates()

    def setup_environment(self):
        self.settings = Settings()
        self.weather_api = OpenWeatherAPI(self.settings.api_key, self.settings.language)
        # Thread pool to move blocking network calls off the Tkinter main thread
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="weather-worker")

    def setup_window(self):
        self.title("Weather Frame")
        self.attributes('-fullscreen', True)
        self.configure(bg='black')
        self.main_frame = tk.Frame(self, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        self.bind('<Escape>', self.on_close)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Hide mouse cursor
        self.config(cursor="none")

    def create_widgets(self):
        # Reuse the same HTTP session used by the API for icon fetching
        self.weather_widgets = WeatherWidgets(self.main_frame, self.settings.language, session=self.weather_api.session)

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
        # Start processing queued UI updates from worker threads
        self.after(100, self.process_ui_queue)

    def update_time(self):
        self.weather_widgets.update_time(datetime.now())
        self.after(1000, self.update_time)

    def cleanup(self):
        gc.collect()  # Force garbage collection
        self.log_system_stats()
        self.after(3600000, self.cleanup)

    def update_weather(self):
        # If there were consecutive errors, wait before retrying (exponential backoff)
        if self.consecutive_errors > 0:
            wait_factor = 2**(min(self.consecutive_errors, 5) - 1)  # Limit exponent to avoid excessive wait
            wait_time_seconds = 300 * wait_factor
            if time.time() - self.last_successful_update < wait_time_seconds:
                logging.info(f"Waiting {wait_time_seconds} seconds before retry due to {self.consecutive_errors} previous errors.")
                self.after(300000, self.update_weather)
                return
            else:
                logging.info(f"Attempting update after waiting period. Consecutive errors: {self.consecutive_errors}")

        if self.is_fetching_weather:
            # Avoid overlapping fetches
            self.after(300000, self.update_weather)
            return

        self.is_fetching_weather = True

        def _fetch() -> WeatherData:
            current_data = self.weather_api.get_current_weather(self.settings.city)
            air_data = self.weather_api.get_air_quality(
                current_data['coord']['lat'],
                current_data['coord']['lon']
            )
            forecast_data = self.weather_api.get_forecast(self.settings.city)
            return WeatherData.from_api_response(current_data, air_data, forecast_data)

        future: Future = self.executor.submit(_fetch)

        def _on_done(fut: Future):
            try:
                weather_data: WeatherData = fut.result()
                def _apply_update():
                    self.weather_widgets.update_weather(weather_data)
                    if self.consecutive_errors > 0:
                        logging.info(f"Weather update successful after {self.consecutive_errors} failures.")
                    else:
                        logging.info("Weather update successful")
                    self.consecutive_errors = 0
                    self.last_successful_update = time.time()
                # Queue for execution on Tk main thread
                self.ui_queue.put(_apply_update)
            except requests.exceptions.RequestException as req_err:
                self.consecutive_errors += 1
                error_type = type(req_err).__name__
                error_msg = str(req_err)
                log_level = logging.WARNING
                if "NameResolutionError" in error_msg:
                    log_level = logging.ERROR
                    logging.error("DNS Resolution failed for api.openweathermap.org. Check network/DNS settings.")
                else:
                    logging.warning(f"API Request failed: {error_msg}")
                logging.log(log_level, f"Error updating weather: {error_msg}")
                logging.log(log_level, f"Full error details: {error_type}")
                logging.log(log_level, f"Consecutive errors: {self.consecutive_errors}")
            except Exception as e:
                self.consecutive_errors += 1
                logging.error(f"Unexpected error during weather update: {str(e)}", exc_info=True)
                logging.error(f"Full error details: {type(e).__name__}")
                logging.error(f"Consecutive errors: {self.consecutive_errors}")
            finally:
                self.is_fetching_weather = False
                # Schedule the next update on the Tk main thread
                self.ui_queue.put(lambda: self.after(300000, self.update_weather))

        # Attach completion callback without blocking main thread
        future.add_done_callback(_on_done)

    def process_ui_queue(self):
        try:
            while True:
                task = self.ui_queue.get_nowait()
                try:
                    task()
                except Exception as e:
                    logging.error(f"Error processing UI task: {str(e)}", exc_info=True)
        except Empty:
            pass
        # Keep polling
        self.after(100, self.process_ui_queue)

    def on_close(self, *_args):
        try:
            if self.executor is not None:
                # Non-blocking shutdown; cancel pending futures where possible
                self.executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        # Destroy the window (ends mainloop)
        try:
            self.destroy()
        except Exception:
            pass

def main():
    try:
        app = WeatherFrame()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Critical error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    main() 