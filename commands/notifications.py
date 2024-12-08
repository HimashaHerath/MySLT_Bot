from config.config import (
    USERNAME, PASSWORD, SUBSCRIBER_ID, TP_NO, ACCOUNT_NO,
    GENERAL_CHANNEL_ID, DAILY_SUMMARY_CHANNEL_ID,
    ALERTS_CHANNEL_ID, BILLS_CHANNEL_ID, ADD_ON_USAGE_CHANNEL_ID,
)
from config.timezone_config import get_current_time
from myslt.api import SLTAPI
from logging_config import setup_logging
import logging
from discord.ext import commands, tasks
from datetime import timedelta
import asyncio
from tasks.spike_detection import detect_spikes
from tasks.summary import daily_summary
from tasks.bills_notify import fetch_bill_info_and_format

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize SLT API
try:
    slt_api = SLTAPI(USERNAME, PASSWORD)
    logger.info("SLTAPI initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize SLTAPI: {e}")
    slt_api = None


class NotificationsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.threshold = None
        logger.info("NotificationsCommands Cog initialized.")

        # Start background tasks
        self.spike_detection_task.start()
        self.daily_summary_task.start()
        self.bills_notification_task.start()
        self.vas_bundles_notification_task.start()

    def cog_unload(self):
        """Cancel all background tasks when the cog is unloaded."""
        self.spike_detection_task.cancel()
        self.daily_summary_task.cancel()
        self.bills_notification_task.cancel()
        self.vas_bundles_notification_task.cancel()
        logger.info("NotificationsCommands Cog unloaded.")

    def get_channel(self, channel_id):
        """Fetch a Discord channel by ID, logging a warning if not found."""
        channel = self.bot.get_channel(channel_id)
        if not channel:
            logger.warning(f"Channel with ID {channel_id} not found.")
        return channel

    def check_api_initialized(self):
        """Check if the SLT API is initialized, raise an error if not."""
        if slt_api is None:
            raise RuntimeError("SLT API is not initialized.")

    async def wait_until_time(self, target_hour, target_minute=0):
        """Wait until a specific time of day."""
        now = get_current_time()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

    # ---- Tasks ----
    @tasks.loop(minutes=5)
    async def spike_detection_task(self):
        """Periodic spike detection task."""
        try:
            self.check_api_initialized()
            usage_diff = 0.5  # Example value
            result = detect_spikes({"usage_diff": usage_diff}, self.threshold)
            if "Spike detected" in result:
                alert_channel = self.get_channel(ALERTS_CHANNEL_ID)
                if alert_channel:
                    await alert_channel.send(result)
                    logger.info("Spike detected and alert sent.")
        except Exception as e:
            logger.error(f"Error in spike_detection_task: {e}")

    @tasks.loop(hours=24)
    async def daily_summary_task(self):
        """Send daily summary at 10:00 PM SLT."""
        try:
            self.check_api_initialized()
            await self.wait_until_time(22, 0)
            api_response = slt_api.get_usage_summary(SUBSCRIBER_ID)
            result = daily_summary(api_response)
            channel = self.get_channel(DAILY_SUMMARY_CHANNEL_ID) or self.get_channel(GENERAL_CHANNEL_ID)
            if channel:
                await channel.send(result)
                logger.info("Daily summary sent.")
        except Exception as e:
            logger.error(f"Error in daily_summary_task: {e}")

    @tasks.loop(hours=24)
    async def bills_notification_task(self):
        """Notify about bills on specific days."""
        try:
            self.check_api_initialized()
            if get_current_time().day in [1, 15]:
                message = fetch_bill_info_and_format(slt_api, TP_NO, ACCOUNT_NO)
                channel = self.get_channel(BILLS_CHANNEL_ID)
                if channel:
                    await channel.send(message)
                    logger.info("Bills notification sent.")
        except Exception as e:
            logger.error(f"Error in bills_notification_task: {e}")

    @tasks.loop(hours=12)
    async def vas_bundles_notification_task(self):
        """Send regular updates about VAS bundles to the ADD_ON_USAGE_CHANNEL_ID."""
        try:
            self.check_api_initialized()
            vas_bundles = slt_api.get_vas_bundles(SUBSCRIBER_ID)
            if not vas_bundles.get("isSuccess"):
                logger.warning("Failed to retrieve VAS bundles for notification.")
                return

            data_bundle = vas_bundles.get("dataBundle", {})
            usage_details = data_bundle.get("usageDetails", [])

            if not usage_details:
                logger.info("No active VAS bundles for notification.")
                return

            channel = self.get_channel(ADD_ON_USAGE_CHANNEL_ID)
            if not channel:
                logger.warning("VAS Bundles Notification Channel not found.")
                return

            # Build the notification message
            message = "**📦 VAS Bundles Update:**\n"
            for detail in usage_details:
                name = detail.get("name", "N/A")
                used = detail.get("used", "0.0")
                expiry = detail.get("expiry_date", "N/A")
                message += (
                    f"- **{name}**\n"
                    f"  - Data Used: {used}GB\n"
                    f"  - Expiry Date: {expiry}\n\n"
                )

            await channel.send(message)
            logger.info("VAS Bundles notification sent successfully.")
        except Exception as e:
            logger.error(f"Error in vas_bundles_notification_task: {e}")

    # ---- Commands ----
    @commands.command(name="spike")
    async def spike_cmd(self, ctx):
        """Manually trigger spike detection."""
        try:
            self.check_api_initialized()
            result = detect_spikes({"usage_diff": 2.0}, self.threshold)
            await ctx.send(result)
            logger.info(f"Spike detection executed by {ctx.author}.")
        except Exception as e:
            logger.error(f"Error in spike_cmd: {e}")
            await ctx.send("An error occurred while detecting spikes.")
            
    @commands.command(name="test_all")
    async def test_all_cmd(self, ctx):
        """
        Test all notifications on-demand:
        - Spike detection (simulated)
        - Daily summary (real API data)
        - Threshold alert (if threshold is set and exceeded)
        - Billing cycle notifications (start and mid)
        - Bills notification (real API data)
        - VAS bundles notification (real API data)
        """
        current_time = get_current_time()
        if slt_api is None:
            await ctx.send("SLT API is not initialized properly.")
            logger.error(f"[{current_time}] SLT API is not initialized. Cannot perform test_all.")
            return
        logger.info(f"[{current_time}] test_all command invoked by {ctx.author}.")
        try:
            # Spike Detection Test
            usage_data_spike = {"usage_diff": 2.5}
            spike_result = detect_spikes(usage_data_spike, self.threshold)
            spike_channel = self.get_channel(ALERTS_CHANNEL_ID) or ctx.channel
            await spike_channel.send(f"**Spike Test:**\n{spike_result}")
            logger.info(f"[{current_time}] Spike Test notification sent.")

            # Daily Summary Test
            api_response_daily = slt_api.get_usage_summary(SUBSCRIBER_ID)
            daily_result = daily_summary(api_response_daily)
            daily_channel = self.get_channel(DAILY_SUMMARY_CHANNEL_ID) or ctx.channel
            await daily_channel.send(f"**Daily Summary Test:**\n{daily_result}")
            logger.info(f"[{current_time}] Daily Summary Test notification sent.")

            # Threshold Alert Test
            if self.threshold is not None:
                usage_data_threshold = {"usage_diff": self.threshold + 1}
                threshold_result = detect_spikes(usage_data_threshold, self.threshold)
                if "Spike detected" in threshold_result:
                    alert_channel = self.get_channel(ALERTS_CHANNEL_ID) or ctx.channel
                    await alert_channel.send(f"**Threshold Alert Test:**\n{threshold_result}")
                    logger.info(f"[{current_time}] Threshold Alert Test notification sent.")
            else:
                await ctx.send("No threshold is set. Set a threshold first using !threshold <value>.")
                logger.warning(f"[{current_time}] Threshold not set for test_all command.")

            # Bills Notification Test
            bills_message = fetch_bill_info_and_format(slt_api, TP_NO, ACCOUNT_NO)
            bills_channel = self.get_channel(BILLS_CHANNEL_ID) or ctx.channel
            await bills_channel.send(f"**Bills Notification Test:**\n{bills_message}")
            logger.info(f"[{current_time}] Bills Notification Test sent.")

            # VAS Bundles Notification Test
            vas_bundles = slt_api.get_vas_bundles(SUBSCRIBER_ID)
            if vas_bundles.get("isSuccess"):
                vas_details = vas_bundles.get("dataBundle", {}).get("usageDetails", [])
                if vas_details:
                    add_on_channel = self.get_channel(ADD_ON_USAGE_CHANNEL_ID) or ctx.channel
                    message = "**📦 VAS Bundles Update (Test):**\n"
                    for detail in vas_details:
                        name = detail.get("name", "N/A")
                        used = detail.get("used", "0.0")
                        expiry = detail.get("expiry_date", "N/A")
                        message += (
                            f"- **{name}**\n"
                            f"  - Data Used: {used}GB\n"
                            f"  - Expiry Date: {expiry}\n\n"
                        )
                    await add_on_channel.send(message)
                    logger.info(f"[{current_time}] VAS Bundles Test notification sent.")
                else:
                    logger.info("No active VAS bundles found for test notification.")
            else:
                logger.warning("Failed to retrieve VAS bundles for test notification.")

            await ctx.send("All test notifications sent!")
            logger.info(f"[{current_time}] test_all command completed successfully.")
        except Exception as e:
            logger.error(f"[{current_time}] Error in test_all_cmd for user {ctx.author}: {e}", exc_info=True)
            await ctx.send("An error occurred while testing all notifications.")

async def setup(bot):
    """
    This function is required for the Discord bot to load the NotificationsCommands cog.
    """
    current_time = get_current_time()
    await bot.add_cog(NotificationsCommands(bot))
    logger.info(f"[{current_time}] NotificationsCommands Cog loaded successfully.")

