import os
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set!")
    sys.exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! Send me a video file and I\'ll convert it to a GIF for you!\n\n'
        'Just upload any video file and I\'ll do the rest.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'This bot converts video files to GIFs.\n\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Show this help message\n\n'
        'Simply send me a video file and I\'ll convert it to a GIF!'
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video files and convert them to GIF."""
    try:
        # Send initial message
        status_message = await update.message.reply_text("🎬 Received your video! Converting to GIF...")
        
        # Get the video file
        video_file = update.message.video or update.message.document
        
        if not video_file:
            await status_message.edit_text("❌ No video file found in your message.")
            return
        
        # Check file size (Telegram limit is 20MB for bots)
        if video_file.file_size > 20 * 1024 * 1024:  # 20MB
            await status_message.edit_text("❌ File too large! Please send a video smaller than 20MB.")
            return
        
        # Update status
        await status_message.edit_text("📥 Downloading video...")
        
        # Download the video file
        file = await video_file.get_file()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
            temp_video_path = temp_video.name
            await file.download_to_drive(temp_video_path)
        
        # Update status
        await status_message.edit_text("🔄 Converting to GIF...")
        
        # Convert video to GIF
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_gif:
            temp_gif_path = temp_gif.name
        
        # Load video and convert to GIF
        video_clip = VideoFileClip(temp_video_path)
        
        # Optimize for GIF conversion
        # Resize if too large (max width 480px for reasonable file size)
        if video_clip.w > 480:
            video_clip = video_clip.resize(width=480)
        
        # Limit duration to 30 seconds for reasonable file size
        if video_clip.duration > 30:
            video_clip = video_clip.subclip(0, 30)
            duration_note = "\n\n⚠️ Video was longer than 30 seconds, so I converted only the first 30 seconds."
        else:
            duration_note = ""
        
        # Convert to GIF with optimized settings
        video_clip.write_gif(
            temp_gif_path,
            fps=10,  # Lower FPS for smaller file size
            opt='OptimizePlus',  # Optimize for smaller file size
            fuzz=1  # Add some fuzziness to reduce file size
        )
        
        # Clean up video clip
        video_clip.close()
        
        # Update status
        await status_message.edit_text("📤 Uploading GIF...")
        
        # Send the GIF
        with open(temp_gif_path, 'rb') as gif_file:
            await update.message.reply_animation(
                animation=gif_file,
                caption=f"✅ Your video has been converted to GIF!{duration_note}"
            )
        
        # Delete status message
        await status_message.delete()
        
        # Clean up temporary files
        os.unlink(temp_video_path)
        os.unlink(temp_gif_path)
        
    except Exception as e:
        logger.error(f"Error converting video: {str(e)}")
        try:
            await status_message.edit_text(
                f"❌ Error converting video: {str(e)}\n\n"
                "Please try with a different video file."
            )
        except:
            await update.message.reply_text(
                f"❌ Error converting video: {str(e)}\n\n"
                "Please try with a different video file."
            )
        
        # Clean up temporary files in case of error
        try:
            if 'temp_video_path' in locals():
                os.unlink(temp_video_path)
            if 'temp_gif_path' in locals():
                os.unlink(temp_gif_path)
        except:
            pass

async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unsupported file types."""
    await update.message.reply_text(
        "❌ I can only convert video files to GIFs.\n\n"
        "Please send me a video file (mp4, avi, mov, etc.)"
    )

def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handle video files
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO, handle_video))
    
    # Handle other file types
    application.add_handler(MessageHandler(filters.PHOTO | filters.AUDIO | filters.Document.ALL, handle_unsupported))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
