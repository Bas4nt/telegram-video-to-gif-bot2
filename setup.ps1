# PowerShell script to set up the development environment
Write-Host "🤖 Setting up Telegram Video to GIF Bot..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check if .env file exists and has bot token
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    if ($envContent -match "your_telegram_bot_token_here") {
        Write-Host "⚠️  Please configure your bot token in the .env file" -ForegroundColor Yellow
        Write-Host "1. Get a bot token from @BotFather on Telegram" -ForegroundColor Cyan
        Write-Host "2. Edit .env file and replace 'your_telegram_bot_token_here' with your actual token" -ForegroundColor Cyan
    } else {
        Write-Host "✅ Bot token appears to be configured!" -ForegroundColor Green
    }
} else {
    Write-Host "❌ .env file not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Setup complete! Run the bot with:" -ForegroundColor Green
Write-Host "python bot.py" -ForegroundColor Cyan
