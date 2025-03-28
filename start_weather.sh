#!/bin/bash

# Change to the project directory
cd /home/pi/raspboard

# Activate virtual environment
source .venv/bin/activate

# Start the weather program
python -m src.main 