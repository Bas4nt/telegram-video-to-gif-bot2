#!/bin/bash

# Exit on error
set -e

echo "Installing system dependencies..."
apt-get update -y
apt-get install -y ffmpeg

echo "Setting up Python environment..."
python -m venv /opt/venv
source /opt/venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies..."
pip install -e .
pip install -r requirements.txt

echo "Testing moviepy import..."
python -c "from moviepy.editor import VideoFileClip; print('MoviePy import successful!')"

echo "Build completed successfully!" 