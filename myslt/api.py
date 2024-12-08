import requests
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SLTAPI:
    BASE_URL = "https://omniscapp.slt.lk/mobitelint/slt/api/"
    CLIENT_ID = "41aed706-8fdf-4b1e-883e-91e44d7f379b"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None  # To track token expiry
        self.login()  # Automatically login on initialization

    def login(self):
        """
        Logs in to the SLT API and retrieves access and refresh tokens.
        """
        url = f"{self.BASE_URL}Account/Login"
        headers = {
            "x-ibm-client-id": self.CLIENT_ID,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://myslt.slt.lk",
            "Referer": "https://myslt.slt.lk/",
            "User-Agent": "Mozilla/5.0",
        }
        payload = {
            "username": self.username,
            "password": self.password,
            "channelID": "WEB",
        }

        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "accessToken" in data and "refreshToken" in data:
                self.access_token = data["accessToken"]
                self.refresh_token = data["refreshToken"]
                expires_in = data.get("expiresIn", 3600)  # Default expiry to 1 hour
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                logger.info("Login successful and token expiry set.")
            else:
                raise Exception("Invalid login response: Missing tokens.")
        else:
            raise Exception(f"Login failed: {response.status_code} {response.text}")

    def _get_headers(self):
        """
        Returns headers for authenticated requests, refreshing the token if necessary.
        """
        if self.access_token and self.token_expiry and datetime.now() >= self.token_expiry:
            logger.info("Access token expired. Refreshing before making the request.")
            self.refresh_access_token()

        if not self.access_token:
            raise Exception("Access token not available. Please log in first.")

        return {
            "x-ibm-client-id": self.CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

    def fetch_data(self, endpoint: str, params: dict = None):
        """
        Generic method to fetch data from a specific endpoint.
        Automatically refreshes the access token if it has expired.
        """
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(2):  # Allow one retry after token refresh
            try:
                response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching data from {endpoint}: {e}")
                if response.status_code == 401 and attempt == 0:
                    logger.info("Access token expired. Refreshing token.")
                    self.refresh_access_token()
                else:
                    raise Exception(f"Failed to fetch data from {endpoint}: {e}")

        raise Exception(f"Failed to fetch data from {endpoint} after retries.")

    def refresh_access_token(self):
        """
        Refreshes the access token using the refresh token.
        """
        if not self.refresh_token:
            raise Exception("Refresh token not available. Please log in first.")

        url = f"{self.BASE_URL}Account/RefreshToken"
        headers = {
            "x-ibm-client-id": self.CLIENT_ID,
            "Content-Type": "application/json",
        }
        payload = {"refreshToken": self.refresh_token}

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("accessToken")
            expires_in = data.get("expiresIn", 3600)  # Default expiry to 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            logger.info("Access token refreshed and expiry updated.")
        else:
            raise Exception(f"Failed to refresh token: {response.status_code} {response.text}")


    def get_usage_summary(self, subscriber_id: str):
        """
        Fetches the usage summary for a given subscriber ID.
        """
        endpoint = "BBVAS/UsageSummary"
        params = {"subscriberID": subscriber_id}
        return self.fetch_data(endpoint, params)

    def get_profile(self, subscriber_id: str):
        """
        Fetches the profile information for a given subscriber ID.
        """
        endpoint = "VAS/GetProfileRequest"
        params = {"subscriberID": subscriber_id}
        return self.fetch_data(endpoint, params)

    def get_bill_status(self, tp_no: str, account_no: str):
        """
        Fetches the bill status for a given telephone number and account number.
        """
        endpoint = "ebill/BillStatusRequest"
        params = {"tpNo": tp_no, "accountNo": account_no}
        return self.fetch_data(endpoint, params)

    def get_extra_gb(self, subscriber_id: str):
        """
        Fetches information about Extra GB for a given subscriber ID.
        """
        endpoint = "BBVAS/ExtraGB"
        params = {"subscriberID": subscriber_id}
        return self.fetch_data(endpoint, params)

    def get_vas_bundles(self, subscriber_id: str):
        """
        Fetches VAS bundles for a given subscriber ID.
        """
        endpoint = "BBVAS/GetDashboardVASBundles"
        params = {"subscriberID": subscriber_id}
        return self.fetch_data(endpoint, params)

    def get_bill_payment_request(self, telephone_no: str, account_no: str):
        """
        Fetches bill payment information for a given telephone number and account number.
        """
        endpoint = "AccountOMNI/BillPaymentRequest"
        params = {"telephoneNo": telephone_no, "accountNo": account_no}
        return self.fetch_data(endpoint, params)
