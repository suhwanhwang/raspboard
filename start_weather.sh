#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Redirect all output to a log so autostart failures are diagnosable
exec >> "$SCRIPT_DIR/autostart.log" 2>&1
echo "=== $(date) autostart start ==="

# Create the virtual environment and install packages only once.
# Doing this on every boot makes startup depend on the network being up,
# which is the main cause of intermittent autostart failures.
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment and installing packages..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your OpenWeather API key and settings"
    exit 1
fi

# Wait for the X display to be ready instead of a fixed sleep.
# A fixed delay races with the desktop on slow boots and the app crashes
# with "couldn't connect to display".
export DISPLAY="${DISPLAY:-:0}"
for i in $(seq 1 60); do
    if xset q >/dev/null 2>&1; then
        echo "X display ready after ${i}s"
        break
    fi
    sleep 1
done

# Start the weather program
python -m src.main
