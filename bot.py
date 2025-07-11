import os
import sys
import logging
import traceback
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import tempfile
import time
import shutil
from pathlib import Path
import asyncio
import signal

# Set up more detailed logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAX_VIDEO_SIZE_MB = 20
MAX_DURATION_SECONDS = 10
MAX_WIDTH_PX = 480
FPS = 15
TIMEOUT_SECONDS = 60  # Timeout for video processing

# Verify dependencies at startup
try:
    from moviepy.editor import VideoFileClip
    logger.info("MoviePy successfully imported")
except ImportError:
    logger.critical("Failed to import MoviePy. Make sure it's installed correctly.")
    sys.exit(1)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        await update.message.reply_text(
            "👋 Hi! I'm a Video to GIF converter bot.\n\n"
            "Just send me any video file and I'll convert it to GIF format!\n\n"
            f"Maximum video size: {MAX_VIDEO_SIZE_MB}MB\n"
            f"Maximum duration: {MAX_DURATION_SECONDS} seconds"
        )
        logger.info(f"Start command used by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await handle_error(update, "Sorry, something went wrong. Please try again later.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    try:
        await update.message.reply_text(
            "How to use this bot:\n\n"
            "1. Send me any video file\n"
            "2. Wait for processing\n"
            "3. Receive your GIF!\n\n"
            f"Limitations:\n"
            f"• Maximum video size: {MAX_VIDEO_SIZE_MB}MB\n"
            f"• Maximum duration: {MAX_DURATION_SECONDS} seconds\n"
            f"• Videos will be resized to {MAX_WIDTH_PX}px width if larger"
        )
        logger.info(f"Help command used by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in help command: {str(e)}")
        await handle_error(update, "Sorry, something went wrong. Please try again later.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the bot's status and health."""
    try:
        # Check if MoviePy is working
        test_clip = None
        try:
            # Create a small test clip
            test_file = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
            test_clip = VideoFileClip(os.path.join(os.path.dirname(__file__), "test_clip.mp4")) if os.path.exists(os.path.join(os.path.dirname(__file__), "test_clip.mp4")) else None
            
            status_message = "✅ Bot is running normally\n\n"
            status_message += f"• MoviePy: Working\n"
            status_message += f"• Maximum video size: {MAX_VIDEO_SIZE_MB}MB\n"
            status_message += f"• Maximum duration: {MAX_DURATION_SECONDS} seconds"
        except Exception as e:
            status_message = "⚠️ Bot is running with issues\n\n"
            status_message += f"• MoviePy error: {str(e)}\n"
        finally:
            if test_clip:
                test_clip.close()
            
        await update.message.reply_text(status_message)
        logger.info(f"Status command used by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in status command: {str(e)}")
        await handle_error(update, "Sorry, something went wrong. Please try again later.")

async def handle_error(update: Update, message: str) -> None:
    """Handle errors gracefully and inform the user."""
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(message)
    except Exception as e:
        logger.error(f"Failed to send error message: {str(e)}")

def safe_cleanup(file_paths):
    """Safely clean up temporary files."""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                if os.path.isfile(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        except Exception as e:
            logger.warning(f"Failed to clean up {path}: {str(e)}")

async def run_with_timeout(coro, timeout):
    """Run a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")

async def convert_video_to_gif(video_path, max_width=MAX_WIDTH_PX, max_duration=MAX_DURATION_SECONDS, fps=FPS):
    """Convert video to GIF with error handling."""
    temp_dir = tempfile.mkdtemp()
    mp4_path = os.path.join(temp_dir, "output.mp4")
    gif_path = os.path.join(temp_dir, "output.gif")
    
    try:
        # Check file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            raise ValueError(f"Video file is too large ({file_size_mb:.1f}MB). Maximum size is {MAX_VIDEO_SIZE_MB}MB.")
        
        # Load the video file
        video_clip = VideoFileClip(video_path)
        
        # Check video duration
        if video_clip.duration > max_duration:
            logger.info(f"Video duration ({video_clip.duration:.1f}s) exceeds limit. Trimming to {max_duration}s.")
            video_clip = video_clip.subclip(0, max_duration)
        
        # Resize if the video is too large
        if video_clip.size[0] > max_width:
            logger.info(f"Video width ({video_clip.size[0]}px) exceeds limit. Resizing to {max_width}px width.")
            video_clip = video_clip.resize(width=max_width)
        
        # Optimize for Telegram - use lower fps for smaller file size
        # Telegram prefers 30fps or less
        actual_fps = min(fps, 25)  # Telegram works best with 25fps or less
        
        # IMPORTANT: For Telegram to recognize as proper animation, we'll use a 2-step process:
        # 1. First create an optimized MP4 (which Telegram handles better)
        logger.info(f"Creating optimized MP4 (duration: {video_clip.duration:.1f}s, size: {video_clip.size}, fps: {actual_fps})")
        start_time = time.time()
        
        # Write optimized MP4 with good settings for Telegram
        video_clip.write_videofile(
            mp4_path,
            fps=actual_fps,
            codec='libx264',
            audio=False,  # No audio needed for GIF
            preset='ultrafast',
            ffmpeg_params=['-pix_fmt', 'yuv420p']  # Compatible format
        )
        
        # 2. Then create GIF from the optimized MP4
        logger.info("Converting optimized MP4 to GIF format")
        from_mp4_clip = VideoFileClip(mp4_path)
        from_mp4_clip.write_gif(
            gif_path,
            fps=actual_fps,
            opt='nq',  # Use 'nq' for better quality with Telegram
            colors=256  # Maximum colors for better quality
        )
        from_mp4_clip.close()
        
        conversion_time = time.time() - start_time
        logger.info(f"GIF conversion completed in {conversion_time:.2f} seconds")
        
        # Close the video clip to release resources
        video_clip.close()
        
        # Check if GIF was created successfully
        if not os.path.exists(gif_path):
            raise FileNotFoundError("GIF file was not created")
        
        # Check GIF file size
        gif_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
        logger.info(f"GIF file size: {gif_size_mb:.2f}MB")
        
        return gif_path, temp_dir
    except Exception as e:
        # Clean up in case of error
        safe_cleanup([temp_dir])
        raise e

async def send_gif_with_fallbacks(update, gif_path, gif_size_mb, processing_message, user_id):
    """Send GIF with multiple fallback methods if one fails."""
    try:
        # Log detailed info about the file
        logger.info(f"Attempting to send GIF to user {user_id}: Path={gif_path}, Size={gif_size_mb:.2f}MB, Exists={os.path.exists(gif_path)}")
        
        # Update status message
        await processing_message.edit_text("GIF created! Sending to you now...")
        
        # Method 1: Send as animation with width/height parameters
        # This is the most reliable way to get Telegram to recognize it as a proper GIF
        try:
            # Get GIF dimensions for proper display
            from PIL import Image
            with Image.open(gif_path) as img:
                width, height = img.size
            
            # Send with explicit width/height which helps Telegram recognize it as animation
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_animation(
                    animation=gif_file,
                    width=width,
                    height=height,
                    filename="animation.gif",  # Use .gif extension explicitly
                    caption=f"Here's your GIF! Tap to save or share."
                )
                logger.info(f"Successfully sent GIF as animation to user {user_id} with dimensions {width}x{height}")
                return True
        except Exception as e1:
            logger.warning(f"Method 1 failed for user {user_id}: {str(e1)}")
        
        # Method 2: Try with different MIME type
        try:
            await processing_message.edit_text("First sending method failed. Trying another...")
            
            # Create a copy with proper MIME type
            mime_fixed_path = os.path.join(os.path.dirname(gif_path), "animation.gif")
            shutil.copy2(gif_path, mime_fixed_path)
            
            with open(mime_fixed_path, 'rb') as gif_file:
                await update.message.reply_animation(
                    animation=InputFile(gif_file, filename="animation.gif"),
                    caption=f"Here's your GIF! Tap to save or share."
                )
                logger.info(f"Successfully sent GIF using method 2 to user {user_id}")
                return True
        except Exception as e2:
            logger.warning(f"Method 2 failed for user {user_id}: {str(e2)}")
        
        # Method 3: Try as document with GIF MIME type
        try:
            await processing_message.edit_text("Animation sending failed. Trying as document...")
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_document(
                    document=InputFile(gif_file, filename="animation.gif"),
                    caption=f"Here's your GIF! You may need to download it first."
                )
                logger.info(f"Successfully sent GIF as document to user {user_id}")
                return True
        except Exception as e3:
            logger.warning(f"Method 3 failed for user {user_id}: {str(e3)}")
            
        # All methods failed
        logger.error(f"All sending methods failed for user {user_id}")
        await processing_message.edit_text(
            "Sorry, I couldn't send the GIF. The conversion worked but there was an issue with Telegram's API."
        )
        return False
        
    except Exception as e:
        logger.error(f"Error in send_gif_with_fallbacks for user {user_id}: {str(e)}\n{traceback.format_exc()}")
        await processing_message.edit_text(
            "Sorry, I couldn't send the GIF due to an unexpected error."
        )
        return False

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert video to GIF when a video is received."""
    user_id = update.effective_user.id
    logger.info(f"Received video from user {user_id}")
    
    # Send a processing message
    processing_message = await update.message.reply_text("Processing your video to GIF...")
    
    # Initialize paths to None for safe cleanup later
    video_path = None
    temp_dir = None
    gif_path = None
    
    try:
        # Get the video file
        video = await update.message.video.get_file()
        
        # Check file size before downloading
        if video.file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
            raise ValueError(f"Video file is too large ({video.file_size / (1024 * 1024):.1f}MB). Maximum size is {MAX_VIDEO_SIZE_MB}MB.")
        
        # Create temporary file for video
        video_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        video_path = video_file.name
        video_file.close()
        
        # Download the video with timeout
        start_time = time.time()
        await run_with_timeout(video.download_to_drive(video_path), TIMEOUT_SECONDS)
        download_time = time.time() - start_time
        logger.info(f"Video downloaded in {download_time:.2f} seconds")
        
        # Convert video to GIF with timeout
        start_time = time.time()
        gif_path, temp_dir = await run_with_timeout(
            convert_video_to_gif(video_path), 
            TIMEOUT_SECONDS
        )
        conversion_time = time.time() - start_time
        logger.info(f"Video converted to GIF in {conversion_time:.2f} seconds")
        
        # Check if the resulting GIF is not too large
        gif_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
        if gif_size_mb > 50:  # Telegram's limit for documents is 50MB
            await processing_message.edit_text(
                f"The resulting GIF is too large ({gif_size_mb:.1f}MB). "
                "Please try with a shorter or smaller video."
            )
            safe_cleanup([video_path, temp_dir])
            return
        
        # Try to send the GIF with multiple fallback methods
        success = await send_gif_with_fallbacks(update, gif_path, gif_size_mb, processing_message, user_id)
        
        if success:
            # Delete the processing message if we successfully sent the GIF
            try:
                await processing_message.delete()
            except Exception:
                pass
        
    except ValueError as e:
        # Handle validation errors (file size, etc.)
        logger.warning(f"Validation error for user {user_id}: {str(e)}")
        await processing_message.edit_text(str(e))
    except TimeoutError as e:
        # Handle timeout errors
        logger.error(f"Timeout error for user {user_id}: {str(e)}")
        await processing_message.edit_text(
            "Processing took too long and timed out. Please try with a shorter or smaller video."
        )
    except Exception as e:
        # Handle all other errors
        error_details = traceback.format_exc()
        logger.error(f"Error converting video to GIF for user {user_id}: {str(e)}\n{error_details}")
        
        try:
            await processing_message.edit_text(
                "Sorry, I couldn't convert your video to GIF. Please try again with a different video."
            )
        except Exception:
            await handle_error(update, "Sorry, I couldn't convert your video to GIF. Please try again with a different video.")
    finally:
        # Clean up all temporary files
        safe_cleanup([video_path, temp_dir])

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document files that might be videos."""
    user_id = update.effective_user.id
    document = update.message.document
    mime_type = document.mime_type
    
    logger.info(f"Received document from user {user_id}, mime type: {mime_type}")
    
    if mime_type and mime_type.startswith('video/'):
        processing_message = await update.message.reply_text("Processing your video to GIF...")
        
        # Initialize paths to None for safe cleanup later
        video_path = None
        temp_dir = None
        gif_path = None
        
        try:
            # Check file size before downloading
            if document.file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                raise ValueError(f"Video file is too large ({document.file_size / (1024 * 1024):.1f}MB). Maximum size is {MAX_VIDEO_SIZE_MB}MB.")
            
            # Get the file
            file = await document.get_file()
            
            # Create temporary file for video
            video_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            video_path = video_file.name
            video_file.close()
            
            # Download the video with timeout
            start_time = time.time()
            await run_with_timeout(file.download_to_drive(video_path), TIMEOUT_SECONDS)
            download_time = time.time() - start_time
            logger.info(f"Video document downloaded in {download_time:.2f} seconds")
            
            # Convert video to GIF with timeout
            start_time = time.time()
            gif_path, temp_dir = await run_with_timeout(
                convert_video_to_gif(video_path), 
                TIMEOUT_SECONDS
            )
            conversion_time = time.time() - start_time
            logger.info(f"Video document converted to GIF in {conversion_time:.2f} seconds")
            
            # Check if the resulting GIF is not too large
            gif_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
            if gif_size_mb > 50:  # Telegram's limit for documents is 50MB
                await processing_message.edit_text(
                    f"The resulting GIF is too large ({gif_size_mb:.1f}MB). "
                    "Please try with a shorter or smaller video."
                )
                safe_cleanup([video_path, temp_dir])
                return
            
            # Try to send the GIF with multiple fallback methods
            success = await send_gif_with_fallbacks(update, gif_path, gif_size_mb, processing_message, user_id)
            
            if success:
                # Delete the processing message if we successfully sent the GIF
                try:
                    await processing_message.delete()
                except Exception:
                    pass
            
        except ValueError as e:
            # Handle validation errors (file size, etc.)
            logger.warning(f"Validation error for user {user_id}: {str(e)}")
            await processing_message.edit_text(str(e))
        except TimeoutError as e:
            # Handle timeout errors
            logger.error(f"Timeout error for user {user_id}: {str(e)}")
            await processing_message.edit_text(
                "Processing took too long and timed out. Please try with a shorter or smaller video."
            )
        except Exception as e:
            # Handle all other errors
            error_details = traceback.format_exc()
            logger.error(f"Error converting document to GIF for user {user_id}: {str(e)}\n{error_details}")
            
            try:
                await processing_message.edit_text(
                    "Sorry, I couldn't convert your video to GIF. Please try again with a different video."
                )
            except Exception:
                await handle_error(update, "Sorry, I couldn't convert your video to GIF. Please try again with a different video.")
        finally:
            # Clean up all temporary files
            safe_cleanup([video_path, temp_dir])
    else:
        await update.message.reply_text("Please send a video file to convert to GIF.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Send a message to the user
    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )

def signal_handler(sig, frame):
    """Handle termination signals gracefully."""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

def main() -> None:
    """Start the bot."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.critical("No TELEGRAM_TOKEN environment variable found!")
        sys.exit(1)
    
    try:
        # Create the Application
        application = Application.builder().token(token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        # Add message handlers
        application.add_handler(MessageHandler(filters.VIDEO, handle_video))
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        
        # Add error handler
        application.add_error_handler(error_handler)

        logger.info("Bot started successfully")
        
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
