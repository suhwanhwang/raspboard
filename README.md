# Weather Frame for Raspberry Pi

A digital weather frame application for Raspberry Pi.

## Features
- Current time and date display
- Current weather information display (temperature, weather condition, icon)
- Automatic weather updates every 5 minutes
- One-week weather forecast display
- Fullscreen mode support
- Multi-language support (English and Korean)
- Modular and extensible architecture

## Project Structure
```
raspboard/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── weather_api.py      # Weather API interface
│   │   └── openweather_api.py  # OpenWeather API implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── weather_data.py     # Data models
│   ├── ui/
│   │   ├── __init__.py
│   │   └── weather_widgets.py  # UI components
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── __init__.py
│   └── main.py                 # Main application
├── .env                        # Environment variables
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
├── start_weather.sh          # Execution script
└── weather-frame.desktop     # Auto-start configuration
```

## Installation

1. Clone the project:
```bash
git clone [repository-url]
cd raspboard
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install Korean font (if using Korean language):
```bash
sudo apt-get update
sudo apt-get install fonts-nanum
```

5. Get OpenWeatherMap API key:
- Sign up at [OpenWeatherMap](https://openweathermap.org/)
- Get your API key

6. Set up environment variables:
- Create `.env` file
```bash
cp .env.example .env
```
- Enter your API key in the `OPENWEATHER_API_KEY` field in `.env` file
- Change `CITY` value to your desired city (default: Seoul)
- Set `LANGUAGE` value to either 'en' for English or 'kr' for Korean (default: kr)

## Manual Execution

With virtual environment activated:
```bash
python -m src.main
```

Or use the execution script:
```bash
./start_weather.sh
```

## Auto-start Configuration

1. Set execution script permissions:
```bash
chmod +x start_weather.sh
```

2. Create autostart directory and copy desktop entry:
```bash
mkdir -p ~/.config/autostart
cp weather-frame.desktop ~/.config/autostart/
```

3. Path configuration:
- Modify the project path in `start_weather.sh` and `weather-frame.desktop` files to match your actual installation path
  - Default path is set to `/home/pi/raspboard`
  - If installed in a different location, update the paths in these files accordingly

## Program Termination
- Press ESC key to exit the program.

## Development

### Adding a New Weather API
The application is designed to be extensible. To add support for a new weather API:

1. Create a new class in `src/api/` that implements the `WeatherAPI` interface
2. Update the configuration to use the new API implementation
3. The rest of the application will work with the new API without modification

### Project Organization
- `src/api/`: Contains API interfaces and implementations
- `src/models/`: Contains data models and data processing logic
- `src/ui/`: Contains UI components and layout management
- `src/config/`: Contains configuration management
- `src/main.py`: Main application entry point

## Notes
- Internet connection is required to run the program.
- Adjust Raspberry Pi's power management settings to prevent screen from turning off.
- Weather information updates automatically every 5 minutes.
- Language can be changed by modifying the `LANGUAGE` value in the `.env` file.

## Troubleshooting
- If Korean text is not displayed: Check if Nanum font is installed
- If weather information is not displayed: Verify API key and internet connection
- If auto-start is not working: Check path configuration and execution permissions
- If language is not changing: Verify the `LANGUAGE` value in `.env` file is set to either 'en' or 'kr'
- If module import errors occur: Ensure you're running the application from the project root directory 