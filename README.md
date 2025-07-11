# Telegram Video to GIF Converter Bot

A simple Telegram bot that converts video files to GIFs, deployed on Railway.

## Features

- 🎬 Converts video files to animated GIFs
- 📱 Works with all common video formats (MP4, AVI, MOV, etc.)
- 🔧 Automatic optimization for reasonable file sizes
- ⚡ Fast processing and upload
- 🚀 Deployed on Railway for 24/7 availability

## How to Use

1. Start a chat with the bot
2. Send the `/start` command to get started
3. Upload any video file
4. Wait for the bot to process and convert your video
5. Download your new GIF!

## Features & Limitations

- **File size limit**: 20MB (Telegram's limit for bots)
- **Duration limit**: Videos longer than 30 seconds are trimmed to the first 30 seconds
- **Auto-resize**: Videos wider than 480px are automatically resized
- **Optimized output**: GIFs are optimized for smaller file sizes

## Setup for Development

### Prerequisites

- Python 3.11+
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))

### Local Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your bot token:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Railway Deployment

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Manual Deployment

1. Create a new Railway project
2. Connect your GitHub repository
3. Add environment variable:
   - `BOT_TOKEN`: Your Telegram bot token
4. Deploy!

Railway will automatically detect the Python environment and install dependencies.

## How to Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat and send `/newbot`
3. Follow the instructions to create your bot
4. Copy the bot token and add it to your environment variables

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | Yes |

## Technical Details

- **Framework**: python-telegram-bot
- **Video Processing**: MoviePy
- **Platform**: Railway
- **Python Version**: 3.11

## Commands

- `/start` - Start the bot and get welcome message
- `/help` - Show help information

## File Structure

```
telegram-video-gif-bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway process file
├── runtime.txt        # Python version specification
├── .env               # Environment variables (local only)
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please create an issue in the GitHub repository.
