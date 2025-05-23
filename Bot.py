import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging
from logging_config import setup_logging

# Initialize enhanced logging with bot-specific configuration
logger = setup_logging(
    log_level=logging.INFO,
    app_name='discord_bot',
    log_dir='logs',
    json_logs=True
)

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
    logger.info(f"Bot is online as {bot.user}", extra={
        'event_type': 'bot_ready',
        'user_id': bot.user.id,
        'username': str(bot.user)
    })
    
    guild_details = [
        {'id': guild.id, 'name': guild.name, 'member_count': guild.member_count}
        for guild in bot.guilds
    ]
    
    logger.info(
        f"Connected to {len(bot.guilds)} guild(s)", 
        extra={
            'event_type': 'guild_connection',
            'guild_count': len(bot.guilds),
            'guilds': guild_details
        }
    )

@bot.event
async def on_disconnect():
    """
    Event triggered when the bot disconnects from Discord.
    """
    logger.warning("Bot has disconnected from Discord", extra={'event_type': 'bot_disconnect'})

@bot.event
async def on_error(event, *args, **kwargs):
    """
    Global error handler for bot events
    """
    logger.error(
        f"Error in event {event}", 
        exc_info=True,
        extra={
            'event_type': 'bot_error',
            'event_name': event
        }
    )

async def setup_extensions():
    """
    Dynamically load extensions (cogs) from a predefined list.
    """
    extensions = ["commands.general", "commands.notifications"]  # Add more extensions as needed
    
    loaded = 0
    failed = 0
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}", extra={
                'event_type': 'extension_loaded',
                'extension': extension
            })
            loaded += 1
        except Exception as e:
            logger.error(
                f"Error loading extension {extension}", 
                exc_info=True,
                extra={
                    'event_type': 'extension_load_failed',
                    'extension': extension,
                    'error': str(e)
                }
            )
            failed += 1
    
    logger.info(
        f"Extension loading complete", 
        extra={
            'event_type': 'extensions_summary',
            'loaded': loaded,
            'failed': failed,
            'total': len(extensions)
        }
    )

async def main():
    """
    Main function to start the bot.
    """
    try:
        async with bot:
            logger.info("Starting bot initialization", extra={'event_type': 'bot_init_start'})
            await setup_extensions()
            logger.info("Starting bot connection", extra={'event_type': 'bot_connect_start'})
            await bot.start(BOT_TOKEN)
    except Exception as e:
        logger.critical(
            "Critical error in bot main loop", 
            exc_info=True,
            extra={
                'event_type': 'bot_critical_error',
                'error': str(e)
            }
        )
        raise

if __name__ == "__main__":
    try:
        logger.info("Bot process starting", extra={'event_type': 'bot_process_start'})
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested via keyboard interrupt", extra={'event_type': 'bot_shutdown_keyboard'})
    except Exception as e:
        logger.error(
            "Unexpected error in bot process", 
            exc_info=True,
            extra={
                'event_type': 'bot_unexpected_error',
                'error': str(e)
            }
        )
