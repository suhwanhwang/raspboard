# Weather Frame for Raspberry Pi

A digital weather frame application for Raspberry Pi.

## Features
- Current time and date display
- Current weather information display (temperature, weather condition, icon)
- Automatic weather updates every 5 minutes
- One-week weather forecast display
- Fullscreen mode support
- Multi-language support (English and Korean)

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
python weather_frame.py
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