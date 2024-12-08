import os

# Environment Variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SUBSCRIBER_ID = os.getenv("SUBSCRIBER_ID")
TP_NO = os.getenv("TP_NO")
ACCOUNT_NO = os.getenv("ACCOUNT_NO")

# Channel IDs
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID", 0))
DAILY_SUMMARY_CHANNEL_ID = int(os.getenv("DAILY_SUMMARY_CHANNEL_ID", 0))
ALERTS_CHANNEL_ID = int(os.getenv("ALERTS_CHANNEL_ID", 0))
WEEKLY_RECAP_CHANNEL_ID = int(os.getenv("WEEKLY_RECAP_CHANNEL_ID", 0))
BILLS_CHANNEL_ID = int(os.getenv("BILLS_CHANNEL_ID", 0))
ADD_ON_USAGE_CHANNEL_ID = int(os.getenv("ADD_ON_USAGE_CHANNEL_ID", 0))

# Validate configuration (optional)
missing_vars = [
    var for var, value in {
        "USERNAME": USERNAME,
        "PASSWORD": PASSWORD,
        "SUBSCRIBER_ID": SUBSCRIBER_ID,
        "TP_NO": TP_NO,
        "ACCOUNT_NO": ACCOUNT_NO,
    }.items()
    if not value
]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
