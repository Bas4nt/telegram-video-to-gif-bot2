# Video to GIF Telegram Bot

A simple Telegram bot that converts video files to GIF format.

## Features

- Converts video files to GIF format
- Handles both video messages and document files
- Automatically resizes large videos
- Limits GIFs to 10 seconds for better performance

## Requirements

- Python 3.8+
- python-telegram-bot
- moviepy
- Pillow

## Setup and Deployment

### Local Development

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your Telegram Bot Token as an environment variable:
   ```
   export TELEGRAM_TOKEN=your_telegram_bot_token
   ```
4. Run the bot:
   ```
   python bot.py
   ```

### Deploy on Railway

1. Create a Railway account at [railway.app](https://railway.app)
2. Create a new project and select "Deploy from GitHub"
3. Connect your GitHub account and select this repository
4. Add the following environment variable:
   - `TELEGRAM_TOKEN`: Your Telegram bot token (get it from [@BotFather](https://t.me/BotFather))
5. Deploy the project

Railway will automatically install dependencies from requirements.txt and start the bot using the Procfile.

## How to Use the Bot

1. Start a chat with your bot on Telegram
2. Send a video file (as video or document)
3. Wait for processing
4. Receive your GIF!

## Notes

- For best results, send videos less than 10MB
- GIFs are limited to 10 seconds to maintain reasonable file sizes
- Videos larger than 480px width will be resized
