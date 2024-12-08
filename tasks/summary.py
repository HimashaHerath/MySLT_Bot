from logging_config import setup_logging
import logging

# Set up logging using the external configuration
setup_logging()
logger = logging.getLogger(__name__)  # Module-specific logger

def extract_usage_details(api_response):
    """
    Extracts and validates usage details from the API response.

    Args:
        api_response (dict): The API response containing usage details.

    Returns:
        dict: A dictionary with extracted usage details or an error message if invalid.
    """
    if not isinstance(api_response, dict) or not api_response.get("isSuccess"):
        logger.error("Invalid or unsuccessful API response.")
        return None

    data_bundle = api_response.get("dataBundle", {})
    package_info = data_bundle.get("my_package_info", {})
    usage_details = package_info.get("usageDetails", [])

    extracted = {"standard_limit": None, "standard_used": None, "total_limit": None, "total_used": None}

    for detail in usage_details:
        name = detail.get("name", "").lower()
        try:
            if "total" in name:
                extracted["total_limit"] = float(detail.get("limit", 0.0))
                extracted["total_used"] = float(detail.get("used", 0.0))
            elif name.strip() == "standard":
                extracted["standard_limit"] = float(detail.get("limit", 0.0))
                extracted["standard_used"] = float(detail.get("used", 0.0))
        except ValueError as e:
            logger.error(f"Error parsing usage detail: {e}", exc_info=True)

    return extracted if all(extracted.values()) else None


def format_summary_message(usage_details):
    """
    Formats usage details into a user-friendly message.

    Args:
        usage_details (dict): Extracted usage details.

    Returns:
        str: A formatted message with usage summary.
    """
    night_limit = usage_details["total_limit"] - usage_details["standard_limit"]
    night_used = max(usage_details["total_used"] - usage_details["standard_used"], 0.0)

    return (
        "Here is your daily data usage summary:\n\n"
        "**Daytime (Standard) Usage:**\n"
        f" - Used: {usage_details['standard_used']}GB out of {usage_details['standard_limit']}GB\n\n"
        "**Nighttime Usage:**\n"
        f" - Used: {night_used}GB out of {night_limit}GB\n\n"
        "**Total (Day + Night):**\n"
        f" - Used: {usage_details['total_used']}GB out of {usage_details['total_limit']}GB\n\n"
    )


def daily_summary(api_response):
    """
    Given a usage summary API response, generate a user-friendly daily summary.

    Args:
        api_response (dict): The API response.

    Returns:
        str: The daily summary message.
    """
    logger.info("Processing daily summary from API response.")
    usage_details = extract_usage_details(api_response)
    if not usage_details:
        return "Error: Could not retrieve or parse usage data."
    return format_summary_message(usage_details)