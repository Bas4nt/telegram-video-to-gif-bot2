import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import tempfile
# Change the import to be more specific
from moviepy.editor import VideoFileClip

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hi! I'm a Video to GIF converter bot.\n\n"
        "Just send me any video file and I'll convert it to GIF format!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send me any video file\n"
        "2. Wait for processing\n"
        "3. Receive your GIF!\n\n"
        "Note: For best results, send videos less than 10MB."
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert video to GIF when a video is received."""
    # Send a processing message
    processing_message = await update.message.reply_text("Processing your video to GIF...")
    
    try:
        # Get the video file
        video = await update.message.video.get_file()
        
        # Create temporary files for video and GIF
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file, \
             tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as gif_file:
            
            video_path = video_file.name
            gif_path = gif_file.name
        
        # Download the video
        await video.download_to_drive(video_path)
        
        # Convert video to GIF using moviepy
        video_clip = VideoFileClip(video_path)
        
        # Resize if the video is too large (optional)
        if video_clip.size[0] > 480:  # If width is greater than 480px
            video_clip = video_clip.resize(width=480)
        
        # Convert to GIF (limit to first 10 seconds if longer)
        if video_clip.duration > 10:
            video_clip = video_clip.subclip(0, 10)
            
        video_clip.write_gif(gif_path, fps=15)
        
        # Send the GIF back to the user
        await update.message.reply_document(
            document=open(gif_path, 'rb'),
            filename="converted.gif",
            caption="Here's your GIF!"
        )
        
        # Delete the processing message
        await processing_message.delete()
        
        # Clean up temporary files
        video_clip.close()
        os.unlink(video_path)
        os.unlink(gif_path)
        
    except Exception as e:
        logger.error(f"Error converting video to GIF: {e}")
        await processing_message.edit_text(
            "Sorry, I couldn't convert your video to GIF. Please try again with a different video."
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document files that might be videos."""
    document = update.message.document
    mime_type = document.mime_type
    
    if mime_type and mime_type.startswith('video/'):
        processing_message = await update.message.reply_text("Processing your video to GIF...")
        
        try:
            # Get the file
            file = await document.get_file()
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file, \
                 tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as gif_file:
                
                video_path = video_file.name
                gif_path = gif_file.name
            
            # Download the video
            await file.download_to_drive(video_path)
            
            # Convert video to GIF using moviepy
            video_clip = VideoFileClip(video_path)
            
            # Resize if the video is too large
            if video_clip.size[0] > 480:
                video_clip = video_clip.resize(width=480)
            
            # Convert to GIF (limit to first 10 seconds if longer)
            if video_clip.duration > 10:
                video_clip = video_clip.subclip(0, 10)
                
            video_clip.write_gif(gif_path, fps=15)
            
            # Send the GIF back to the user
            await update.message.reply_document(
                document=open(gif_path, 'rb'),
                filename="converted.gif",
                caption="Here's your GIF!"
            )
            
            # Delete the processing message
            await processing_message.delete()
            
            # Clean up temporary files
            video_clip.close()
            os.unlink(video_path)
            os.unlink(gif_path)
            
        except Exception as e:
            logger.error(f"Error converting video to GIF: {e}")
            await processing_message.edit_text(
                "Sorry, I couldn't convert your video to GIF. Please try again with a different video."
            )
    else:
        await update.message.reply_text("Please send a video file to convert to GIF.")

def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("No TELEGRAM_TOKEN environment variable found!")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
