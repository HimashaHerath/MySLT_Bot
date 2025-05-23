import asyncio
import logging
import multiprocessing
import subprocess
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("runner")

def run_api_server():
    """Runs the FastAPI server in a separate process"""
    logger.info("Starting FastAPI server...")
    # Use subprocess instead of direct uvicorn.run to avoid signal handler issues
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.app:app", "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"API server process failed: {e}")
    except KeyboardInterrupt:
        logger.info("API server stopped via keyboard interrupt")

async def run_discord_bot():
    """Runs the Discord bot"""
    logger.info("Starting Discord bot...")
    try:
        # Import bot-related modules here to avoid circular imports
        from Bot import main
        await main()
    except Exception as e:
        logger.error(f"Error in Discord bot: {e}", exc_info=True)

async def main():
    """Main function to run both services"""
    # Start the API server in a separate process
    api_process = multiprocessing.Process(target=run_api_server)
    api_process.daemon = True
    api_process.start()
    logger.info(f"API server process started (PID: {api_process.pid})")

    # Run the Discord bot in the main thread
    try:
        await run_discord_bot()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Try to terminate the API process gracefully
        if api_process.is_alive():
            logger.info("Terminating API server process...")
            api_process.terminate()
            api_process.join(timeout=3)
            if api_process.is_alive():
                logger.warning("API process didn't terminate gracefully, forcing...")
                api_process.kill()

if __name__ == "__main__":
    # Enable multiprocessing for Windows if needed
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 