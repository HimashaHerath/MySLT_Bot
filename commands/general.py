from config.config import USERNAME, PASSWORD, SUBSCRIBER_ID, TP_NO, ACCOUNT_NO
from config.timezone_config import get_current_time
from myslt.api import SLTAPI
from logging_config import setup_logging
import logging
from discord.ext import commands
import traceback

# Set up logging
logger = logging.getLogger(__name__)  # Module-specific logger

# Initialize SLT API
try:
    slt_api = SLTAPI(USERNAME, PASSWORD)
    logger.info("SLTAPI initialized successfully", extra={'event_type': 'slt_api_init_success'})
except Exception as e:
    logger.critical(
        "Failed to initialize SLTAPI", 
        exc_info=True,
        extra={
            'event_type': 'slt_api_init_failed',
            'error': str(e),
            'error_type': type(e).__name__
        }
    )
    slt_api = None  # Handle gracefully in commands


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("GeneralCommands Cog initialized", extra={'event_type': 'cog_init'})

    def check_slt_api(self):
        """Helper method to validate SLT API initialization."""
        if slt_api is None:
            raise RuntimeError("SLT API is not initialized.")

    def log_command(self, ctx, command_name):
        """Helper method to log command execution with structured data."""
        logger.info(
            f"{command_name} command executed", 
            extra={
                'event_type': 'command_executed',
                'command': command_name,
                'user_id': str(ctx.author.id),
                'username': str(ctx.author),
                'guild_id': str(ctx.guild.id) if ctx.guild else None,
                'guild_name': str(ctx.guild) if ctx.guild else None,
                'channel_id': str(ctx.channel.id),
                'channel_name': str(ctx.channel)
            }
        )

    @commands.command(name="usage")
    async def usage(self, ctx):
        """Command to fetch and display data usage."""
        command_name = "usage"
        self.log_command(ctx, command_name)
        
        try:
            self.check_slt_api()
            
            logger.debug(
                "Fetching usage data from SLT API", 
                extra={
                    'event_type': 'slt_api_call_start',
                    'api_method': 'get_usage_summary',
                    'command': command_name,
                    'user_id': str(ctx.author.id)
                }
            )
            
            usage = slt_api.get_usage_summary(SUBSCRIBER_ID)
            
            if not usage.get("isSuccess", False):
                logger.error(
                    "SLT API usage request unsuccessful", 
                    extra={
                        'event_type': 'slt_api_call_failed',
                        'api_method': 'get_usage_summary',
                        'command': command_name,
                        'response_status': usage.get("status", "unknown"),
                        'user_id': str(ctx.author.id)
                    }
                )
                await ctx.send("Failed to retrieve usage data. The SLT API returned an unsuccessful response.")
                return
                
            used = usage['dataBundle']['my_package_summary']['used']
            limit = usage['dataBundle']['my_package_summary']['limit']
            
            logger.debug(
                "Usage data retrieved successfully", 
                extra={
                    'event_type': 'slt_api_call_success',
                    'api_method': 'get_usage_summary',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'used': used, 
                    'limit': limit
                }
            )
            
            await ctx.send(f"Usage: {used}GB out of {limit}GB.")
            
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning(
                "Usage command failed: SLT API is not initialized", 
                extra={
                    'event_type': 'command_runtime_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e)
                }
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(
                f"Error executing {command_name} command", 
                exc_info=True,
                extra={
                    'event_type': 'command_execution_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_trace
                }
            )
            await ctx.send("An error occurred while fetching usage data.")

    @commands.command(name="profile")
    async def profile(self, ctx):
        """Command to fetch and display user profile."""
        command_name = "profile"
        self.log_command(ctx, command_name)
        
        try:
            self.check_slt_api()
            
            logger.debug(
                "Fetching profile data from SLT API", 
                extra={
                    'event_type': 'slt_api_call_start',
                    'api_method': 'get_profile',
                    'command': command_name,
                    'user_id': str(ctx.author.id)
                }
            )
            
            profile = slt_api.get_profile(SUBSCRIBER_ID)
            
            if not profile.get("isSuccess", False):
                logger.error(
                    "SLT API profile request unsuccessful", 
                    extra={
                        'event_type': 'slt_api_call_failed',
                        'api_method': 'get_profile',
                        'command': command_name,
                        'response_status': profile.get("status", "unknown"),
                        'user_id': str(ctx.author.id)
                    }
                )
                await ctx.send("Failed to retrieve profile data. The SLT API returned an unsuccessful response.")
                return
                
            fullname = profile['dataBundle']['fullname']
            package = profile['dataBundle']['subscriber_package_display']
            
            logger.debug(
                "Profile data retrieved successfully", 
                extra={
                    'event_type': 'slt_api_call_success',
                    'api_method': 'get_profile',
                    'command': command_name,
                    'user_id': str(ctx.author.id)
                }
            )
            
            await ctx.send(f"Profile: {fullname}, Package: {package}")
            
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning(
                "Profile command failed: SLT API is not initialized", 
                extra={
                    'event_type': 'command_runtime_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e)
                }
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(
                f"Error executing {command_name} command", 
                exc_info=True,
                extra={
                    'event_type': 'command_execution_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_trace
                }
            )
            await ctx.send("An error occurred while fetching the profile.")

    @commands.command(name="bill")
    async def bill(self, ctx):
        """Command to fetch and display bill status."""
        command_name = "bill"
        self.log_command(ctx, command_name)
        
        try:
            self.check_slt_api()
            
            logger.debug(
                "Fetching bill data from SLT API", 
                extra={
                    'event_type': 'slt_api_call_start',
                    'api_method': 'get_bill_status',
                    'command': command_name,
                    'user_id': str(ctx.author.id)
                }
            )
            
            bill_status = slt_api.get_bill_status(TP_NO, ACCOUNT_NO)
            
            if not bill_status.get("isSuccess", False):
                logger.error(
                    "SLT API bill status request unsuccessful", 
                    extra={
                        'event_type': 'slt_api_call_failed',
                        'api_method': 'get_bill_status',
                        'command': command_name,
                        'response_status': bill_status.get("status", "unknown"),
                        'user_id': str(ctx.author.id)
                    }
                )
                await ctx.send("Failed to retrieve bill data. The SLT API returned an unsuccessful response.")
                return
                
            desc = bill_status['dataBundle']['bill_code_desc']
            
            logger.debug(
                "Bill data retrieved successfully", 
                extra={
                    'event_type': 'slt_api_call_success',
                    'api_method': 'get_bill_status',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'bill_status': desc
                }
            )
            
            await ctx.send(f"Bill status: {desc}")
            
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning(
                "Bill command failed: SLT API is not initialized", 
                extra={
                    'event_type': 'command_runtime_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e)
                }
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(
                f"Error executing {command_name} command", 
                exc_info=True,
                extra={
                    'event_type': 'command_execution_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_trace
                }
            )
            await ctx.send("An error occurred while fetching the bill status.")

    @commands.command(name="add_on")
    async def vas(self, ctx):
        """Command to fetch and display VAS bundles information."""
        command_name = "add_on"
        self.log_command(ctx, command_name)
        
        try:
            self.check_slt_api()
            
            logger.debug(
                "Fetching VAS data from SLT API", 
                extra={
                    'event_type': 'slt_api_call_start',
                    'api_method': 'get_vas_bundles',
                    'command': command_name,
                    'user_id': str(ctx.author.id)
                }
            )
            
            vas_bundles = slt_api.get_vas_bundles(SUBSCRIBER_ID)
            
            if not vas_bundles.get("isSuccess", False):
                logger.error(
                    "SLT API VAS bundles request unsuccessful", 
                    extra={
                        'event_type': 'slt_api_call_failed',
                        'api_method': 'get_vas_bundles',
                        'command': command_name,
                        'response_status': vas_bundles.get("status", "unknown"),
                        'user_id': str(ctx.author.id)
                    }
                )
                await ctx.send("Error: Unable to retrieve VAS bundles information.")
                return

            data_bundle = vas_bundles.get("dataBundle", {})
            usage_details = data_bundle.get("usageDetails", [])

            if not usage_details:
                logger.info(
                    "No active VAS bundles found", 
                    extra={
                        'event_type': 'vas_bundles_empty',
                        'command': command_name,
                        'user_id': str(ctx.author.id)
                    }
                )
                await ctx.send("No active VAS bundles found.")
                return

            # Build the response message
            message = "**Active VAS Bundles:**\n"
            for detail in usage_details:
                name = detail.get("name", "N/A")
                used = detail.get("used", "0.0")
                expiry = detail.get("expiry_date", "N/A")
                message += (
                    f"- **{name}**\n"
                    f"  - Used: {used}GB\n"
                    f"  - Expires: {expiry}\n\n"
                )
            
            logger.debug(
                "VAS bundles data retrieved successfully", 
                extra={
                    'event_type': 'slt_api_call_success',
                    'api_method': 'get_vas_bundles',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'bundles_count': len(usage_details)
                }
            )

            await ctx.send(message)
            
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning(
                "VAS command failed: SLT API is not initialized", 
                extra={
                    'event_type': 'command_runtime_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e)
                }
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(
                f"Error executing {command_name} command", 
                exc_info=True,
                extra={
                    'event_type': 'command_execution_error',
                    'command': command_name,
                    'user_id': str(ctx.author.id),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_trace
                }
            )
            await ctx.send("An error occurred while retrieving VAS bundles information.")


async def setup(bot):
    """Register the cog with the bot."""
    await bot.add_cog(GeneralCommands(bot))
    logger.info("GeneralCommands Cog loaded", extra={'event_type': 'cog_loaded', 'cog': 'GeneralCommands'})
