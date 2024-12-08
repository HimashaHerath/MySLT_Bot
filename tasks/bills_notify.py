from myslt.api import SLTAPI
from logging_config import setup_logging
from config.timezone_config import get_current_time
import logging
from typing import Optional

# Set up logging using the external configuration
setup_logging()
logger = logging.getLogger(__name__)  # Module-specific logger


def fetch_bill_info(slt_api: SLTAPI, tp_no: str, account_no: str) -> Optional[dict]:
    """
    Fetches bill information from the SLT API.

    Args:
        slt_api (SLTAPI): An instance of the SLTAPI class.
        tp_no (str): The telephone number.
        account_no (str): The account number.

    Returns:
        Optional[dict]: The bill data from the API if successful, or None if the request failed.
    """
    try:
        bill_info = slt_api.get_bill_payment_request(tp_no, account_no)
        if not bill_info.get("isSuccess"):
            logger.error("Failed to retrieve bill payment information from SLT API.")
            return None
        return bill_info.get("dataBundle", {})
    except Exception as e:
        logger.error(f"Error fetching bill information: {e}", exc_info=True)
        return None


def format_bill_info(data: dict) -> str:
    """
    Formats the bill data into a user-friendly message.

    Args:
        data (dict): The bill data.

    Returns:
        str: A formatted message with bill details or an error message.
    """
    billing_list = data.get("listofbillingInquiryType", [])
    if not billing_list:
        logger.warning("No billing information available.")
        return "No billing information available."

    # Extract the first bill
    first_bill = billing_list[0]
    bill_amount = first_bill.get("billAmount", "N/A")
    due_date = first_bill.get("paymentDueDate", "N/A")
    outstanding_balance = first_bill.get("outstandingBalance", "N/A")

    logger.info(
        f"Bill retrieved: Amount = LKR {bill_amount}, Due Date = {due_date}, "
        f"Outstanding Balance = LKR {outstanding_balance}."
    )

    return (
        f"**Bill Payment Reminder**\n"
        f"Current Bill Amount: LKR {bill_amount}\n"
        f"Payment Due Date: {due_date}\n"
        f"Outstanding Balance: LKR {outstanding_balance}\n\n"
        "Please ensure timely payment to avoid any interruption in service."
    )


def fetch_bill_info_and_format(slt_api: SLTAPI, tp_no: str, account_no: str) -> str:
    """
    Fetches and formats bill payment information for notifications.

    Args:
        slt_api (SLTAPI): An instance of the SLTAPI class.
        tp_no (str): The telephone number.
        account_no (str): The account number.

    Returns:
        str: A formatted message with bill details or an error message.
    """
    logger.info("Fetching bill information...")
    data = fetch_bill_info(slt_api, tp_no, account_no)
    if not data:
        return "Could not retrieve the bill payment information."
    return format_bill_info(data)
