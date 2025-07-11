# Deployment Guide

## Railway Deployment Steps

### 1. Prepare Your Bot

1. **Get a Telegram Bot Token**:
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Deploy to Railway

#### Option A: One-Click Deploy (Recommended)
1. Click the "Deploy on Railway" button in the README
2. Connect your GitHub account
3. Fork/import this repository
4. Set the environment variable `BOT_TOKEN` to your bot token
5. Deploy!

#### Option B: Manual Deploy
1. Go to [Railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub and select this repository
4. In the project settings, add environment variable:
   - Key: `BOT_TOKEN`
   - Value: Your actual bot token
5. Railway will automatically deploy

### 3. Configure Your Bot

1. **Set Bot Commands** (optional):
   - Go to [@BotFather](https://t.me/botfather)
   - Send `/setcommands`
   - Select your bot
   - Send:
     ```
     start - Start the bot
     help - Show help information
     ```

2. **Set Bot Description** (optional):
   - Send `/setdescription` to @BotFather
   - Select your bot
   - Enter: "Convert your video files to GIFs easily!"

### 4. Test Your Bot

1. Search for your bot on Telegram (use the username you created)
2. Send `/start`
3. Upload a video file
4. Wait for conversion and download your GIF!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | ✅ Yes |

## Troubleshooting

### Bot Not Responding
- Check that `BOT_TOKEN` is set correctly in Railway
- Verify the bot token is valid in @BotFather
- Check Railway logs for errors

### Conversion Errors
- Ensure video file is under 20MB
- Try with different video formats
- Check Railway logs for specific error messages

### Deployment Issues
- Ensure all files are in the repository
- Check that `requirements.txt` includes all dependencies
- Verify `Procfile` has the correct start command

## Railway Features Used

- **Automatic Deployment**: Deploys on every git push
- **Environment Variables**: Secure token storage
- **Logs**: Real-time application logs
- **Custom Domains**: Optional custom domain support
- **Zero-Config**: Automatic Python environment detection

## Cost

Railway offers:
- **Free Tier**: $5 credit monthly (usually sufficient for small bots)
- **Pro Plan**: $20/month for higher usage

Most personal video conversion bots will run fine on the free tier.
