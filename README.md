
# MySLT Bot

MySLT Bot is a Discord bot that integrates with the SLT API to provide various features, such as data usage tracking, bill notifications, and VAS (Value-Added Services) updates. 

## Features

1. **Data Usage Tracking**:
   - Fetch your data usage and display it in Discord using the `!usage` command.

2. **Profile Information**:
   - Retrieve and display your SLT profile information using the `!profile` command.

3. **Bill Status Notifications**:
   - Get your bill status via the `!bill` command.

4. **VAS (Value-Added Services) Updates**:
   - Use the `!add_on` command to fetch details about active VAS bundles, including data usage and expiry dates.

5. **Automated Notifications**:
   - Regular updates for VAS bundles, daily usage summaries, and bill reminders.

6. **Spike Detection**:
   - Detect unusual spikes in data usage and receive alerts.

7. **Test All Command**:
   - Test all features of the bot using the `!test_all` command.

## Folder Structure

```plaintext
MySLT_Bot/
├── commands/
│   ├── general.py          # Handles user commands like usage, profile, and bill.
│   ├── notifications.py    # Handles automated notifications and scheduled tasks.
├── config/
│   ├── config.py           # Stores configuration constants like API keys and channel IDs.
│   ├── timezone_config.py  # Utility for timezone management (e.g., SLT timezone).
├── myslt/
│   ├── api.py              # Contains the SLT API integration logic.
├── tasks/
│   ├── bills_notify.py     # Handles bill notification tasks.
│   ├── spike_detection.py  # Detects spikes in data usage.
│   ├── summary.py          # Generates daily summaries of data usage.
├── .env                    # Environment variables (e.g., API credentials, bot token).
├── .gitignore              # Ignores unnecessary files in version control.
├── bot.py                  # Main bot entry point.
├── logging_config.py       # Sets up logging configuration for the bot.
├── Dockerfile              # Docker configuration for deploying the bot.
├── requirements.txt        # Python dependencies for the bot.
```

## Installation

### Prerequisites
- Python 3.9+
- Discord Bot Token
- SLT API credentials

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/MySLT_Bot.git
   cd MySLT_Bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file with your credentials:
   ```plaintext
   BOT_TOKEN=your_discord_bot_token
   USERNAME=your_slt_username
   PASSWORD=your_slt_password
   SUBSCRIBER_ID=your_subscriber_id
   TP_NO=your_tp_no
   ACCOUNT_NO=your_account_no
   GENERAL_CHANNEL_ID=your_general_channel_id
   DAILY_SUMMARY_CHANNEL_ID=your_daily_summary_channel_id
   ALERTS_CHANNEL_ID=your_alerts_channel_id
   BILLS_CHANNEL_ID=your_bills_channel_id
   ADD_ON_USAGE_CHANNEL_ID=your_add_on_usage_channel_id
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

- Use `!usage` to check data usage.
- Use `!profile` to view profile information.
- Use `!bill` to check the bill status.
- Use `!add_on` to get VAS bundle updates.
- Use `!test_all` to test all bot functionalities.

## Deployment

You can deploy the bot using Docker:

1. Build the Docker image:
   ```bash
   docker build -t my_slt_bot_image .
   ```

2. Run the Docker container:
   ```bash
   docker run --name MySLT_Bot my_slt_bot_image
   ```

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request for review.

