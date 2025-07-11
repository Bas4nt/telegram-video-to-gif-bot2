#!/usr/bin/env python3
"""
Setup script for the Telegram Video to GIF Bot
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def check_bot_token():
    """Check if bot token is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        print("❌ Bot token not configured!")
        print("Please:")
        print("1. Get a bot token from @BotFather on Telegram")
        print("2. Edit the .env file and replace 'your_telegram_bot_token_here' with your actual token")
        return False
    
    print("✅ Bot token is configured!")
    return True

def main():
    """Main setup function"""
    print("🤖 Telegram Video to GIF Bot Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check bot token
    if not check_bot_token():
        print("\n⚠️  Setup incomplete. Please configure your bot token.")
        sys.exit(1)
    
    print("\n🎉 Setup complete! You can now run the bot with:")
    print("python bot.py")

if __name__ == "__main__":
    main()
