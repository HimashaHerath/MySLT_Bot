from logging_config import setup_logging
from config.timezone_config import get_current_time
import logging

# Set up logging using the external configuration
setup_logging()
logger = logging.getLogger(__name__)  # Module-specific logger

def detect_spikes(usage_data, threshold=None):
    """
    Detect large usage spikes over a short period (e.g., 5 minutes).

    Args:
        usage_data (dict): Must contain 'usage_diff' (float) representing GB increase since last check.
        threshold (float, optional): Custom threshold for spike detection. Defaults to 1.0GB.

    Returns:
        str: Message indicating whether a spike was detected.
    """
    # Validate input
    if not isinstance(usage_data, dict) or "usage_diff" not in usage_data:
        logger.error("Invalid usage_data provided. Expected a dictionary with a 'usage_diff' key.")
        return "Invalid data provided for spike detection."

    usage_diff = usage_data.get("usage_diff", 0.0)
    current_time = get_current_time()
    logger.info(f"Detecting spikes at {current_time}. Usage difference: {usage_diff}GB.")

    # Use the provided threshold or a default value
    threshold = threshold if threshold is not None else 1.0
    logger.debug(f"Using threshold: {threshold}GB.")

    # Determine if a spike occurred
    if usage_diff > threshold:
        logger.warning(f"Spike detected! Usage: {usage_diff}GB exceeds threshold: {threshold}GB.")
        return (
            f"Spike detected! Your usage increased by {usage_diff}GB in the last interval, "
            f"which is above the threshold of {threshold}GB. Please check your activity."
        )

    logger.info(f"No spike detected. Usage: {usage_diff}GB is within the threshold of {threshold}GB.")
    return f"No spike detected. Usage: {usage_diff}GB is within the safe limit of {threshold}GB."
