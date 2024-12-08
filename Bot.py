import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging
from logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)  # Get the logger for this module

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is missing. Please check your .env file.")
    exit(1)

def get_bot():
    """
    Configures and returns the bot instance.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    return commands.Bot(command_prefix="!", intents=intents)

bot = get_bot()

@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready and connected to Discord.
    """
    logger.info(f"Bot is online as {bot.user}")
    logger.info(f"Connected to {len(bot.guilds)} guild(s).")

@bot.event
async def on_disconnect():
    """
    Event triggered when the bot disconnects from Discord.
    """
    logger.warning("Bot has disconnected from Discord.")

async def setup_extensions():
    """
    Dynamically load extensions (cogs) from a predefined list.
    """
    extensions = ["commands.general", "commands.notifications"]  # Add more extensions as needed
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.error(f"Error loading {extension}: {e}", exc_info=True)

async def main():
    """
    Main function to start the bot.
    """
    try:
        async with bot:
            await setup_extensions()
            await bot.start(BOT_TOKEN)
    except Exception as e:
        logger.critical(f"Critical error in bot main loop: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested via keyboard interrupt.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
