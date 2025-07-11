# PowerShell script to run the bot
Write-Host "🚀 Starting Telegram Video to GIF Bot..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
try {
    python -c "import telegram, moviepy, dotenv" 2>$null
    Write-Host "✅ Dependencies verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Dependencies not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "🤖 Bot is starting..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Cyan
Write-Host ""

# Run the bot
python bot.py
