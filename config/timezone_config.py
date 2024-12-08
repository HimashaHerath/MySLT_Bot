from datetime import datetime
import pytz

# Define the timezone for Sri Lanka
SRI_LANKA_TZ = pytz.timezone('Asia/Colombo')

# Get the current time in Sri Lanka
def get_current_time():
    """
    Returns the current date and time in Sri Lanka timezone.
    """
    return datetime.now(SRI_LANKA_TZ)

# Convert a UTC datetime to Sri Lanka timezone
def to_sri_lanka_time(utc_dt):
    """
    Converts a UTC datetime object to Sri Lanka timezone.
    
    Args:
        utc_dt (datetime): A UTC datetime object.
    
    Returns:
        datetime: A datetime object converted to Sri Lanka timezone.
    """
    return utc_dt.astimezone(SRI_LANKA_TZ)

# Convert a Sri Lanka datetime to UTC
def to_utc(sri_lanka_dt):
    """
    Converts a Sri Lanka datetime object to UTC.
    
    Args:
        sri_lanka_dt (datetime): A datetime object in Sri Lanka timezone.
    
    Returns:
        datetime: A UTC datetime object.
    """
    return sri_lanka_dt.astimezone(pytz.utc)
