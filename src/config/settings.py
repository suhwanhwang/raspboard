import os
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.city = os.getenv('CITY', 'Seoul')
        self.language = os.getenv('LANGUAGE', 'kr')

        if not self.api_key:
            raise ValueError("OpenWeather API key not found in .env file!") 