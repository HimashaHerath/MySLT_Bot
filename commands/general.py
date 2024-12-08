from config.config import USERNAME, PASSWORD, SUBSCRIBER_ID, TP_NO, ACCOUNT_NO
from config.timezone_config import get_current_time
from myslt.api import SLTAPI
from logging_config import setup_logging
import logging
from discord.ext import commands

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)  # Module-specific logger

# Initialize SLT API
try:
    slt_api = SLTAPI(USERNAME, PASSWORD)
    logger.info("SLTAPI initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize SLTAPI: {e}")
    slt_api = None  # Handle gracefully in commands


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("GeneralCommands Cog initialized.")

    def check_slt_api(self):
        """Helper method to validate SLT API initialization."""
        if slt_api is None:
            raise RuntimeError("SLT API is not initialized.")

    @commands.command(name="usage")
    async def usage(self, ctx):
        """Command to fetch and display data usage."""
        try:
            self.check_slt_api()
            usage = slt_api.get_usage_summary(SUBSCRIBER_ID)
            used = usage['dataBundle']['my_package_summary']['used']
            limit = usage['dataBundle']['my_package_summary']['limit']
            await ctx.send(f"Usage: {used}GB out of {limit}GB.")
            logger.info(f"Usage command executed by {ctx.author}.")
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning("Usage command failed: SLT API is not initialized.")
        except Exception as e:
            logger.error(f"Error fetching usage: {e}")
            await ctx.send("An error occurred while fetching usage.")

    @commands.command(name="profile")
    async def profile(self, ctx):
        """Command to fetch and display user profile."""
        try:
            self.check_slt_api()
            profile = slt_api.get_profile(SUBSCRIBER_ID)
            fullname = profile['dataBundle']['fullname']
            package = profile['dataBundle']['subscriber_package_display']
            await ctx.send(f"Profile: {fullname}, Package: {package}")
            logger.info(f"Profile command executed by {ctx.author}.")
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning("Profile command failed: SLT API is not initialized.")
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            await ctx.send("An error occurred while fetching the profile.")

    @commands.command(name="bill")
    async def bill(self, ctx):
        """Command to fetch and display bill status."""
        try:
            self.check_slt_api()
            bill_status = slt_api.get_bill_status(TP_NO, ACCOUNT_NO)
            desc = bill_status['dataBundle']['bill_code_desc']
            await ctx.send(f"Bill status: {desc}")
            logger.info(f"Bill command executed by {ctx.author}.")
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning("Bill command failed: SLT API is not initialized.")
        except Exception as e:
            logger.error(f"Error fetching bill status: {e}")
            await ctx.send("An error occurred while fetching the bill status.")

    @commands.command(name="add_on")
    async def vas(self, ctx):
        """Command to fetch and display VAS bundles information."""
        try:
            self.check_slt_api()
            vas_bundles = slt_api.get_vas_bundles(SUBSCRIBER_ID)
            if not vas_bundles.get("isSuccess"):
                await ctx.send("Error: Unable to retrieve VAS bundles information.")
                logger.error("Failed to retrieve VAS bundles from SLT API.")
                return

            data_bundle = vas_bundles.get("dataBundle", {})
            usage_details = data_bundle.get("usageDetails", [])

            if not usage_details:
                await ctx.send("No active VAS bundles found.")
                logger.info("No active VAS bundles found for the user.")
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

            await ctx.send(message)
            logger.info(f"VAS command executed by {ctx.author}.")
        except RuntimeError as e:
            await ctx.send(str(e))
            logger.warning("VAS command failed: SLT API is not initialized.")
        except Exception as e:
            logger.error(f"Error fetching VAS bundles: {e}")
            await ctx.send("An error occurred while retrieving VAS bundles information.")


async def setup(bot):
    """Register the cog with the bot."""
    await bot.add_cog(GeneralCommands(bot))
    logger.info("GeneralCommands Cog loaded.")
