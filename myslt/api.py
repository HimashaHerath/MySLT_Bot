import requests
from dotenv import load_dotenv
import os
import logging
import json
from datetime import datetime, timedelta
from logging_config import setup_logging

# Load environment variables
load_dotenv()

# Configure enhanced logging for the SLT API module
logger = logging.getLogger(__name__)

class SLTAPI:
    BASE_URL = "https://omniscapp.slt.lk/slt/ext/api/"
    CLIENT_ID = "b7402e9d66808f762ccedbe42c20668e"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None  # To track token expiry
        
        logger.info(
            "Initializing SLTAPI client", 
            extra={
                'event_type': 'slt_api_init',
                'username': self.username[:3] + '***' if self.username else None  # Partial logging for privacy
            }
        )
        
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
            "password": "********",  # Masked for logging
            "channelID": "WEB",
        }
        
        # Log attempt with masked credentials
        logger.info(
            "Attempting SLT API login", 
            extra={
                'event_type': 'slt_api_login_attempt',
                'username': self.username[:3] + '***' if self.username else None,
                'api_endpoint': 'Account/Login'
            }
        )
        
        # Create actual payload for the request
        actual_payload = {
            "username": self.username,
            "password": self.password,
            "channelID": "WEB",
        }
        
        try:
            response = requests.post(url, headers=headers, data=actual_payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "accessToken" in data and "refreshToken" in data:
                self.access_token = data["accessToken"]
                self.refresh_token = data["refreshToken"]
                expires_in = data.get("expiresIn", 3600)  # Default expiry to 1 hour
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(
                    "Login successful", 
                    extra={
                        'event_type': 'slt_api_login_success',
                        'token_expiry': self.token_expiry.isoformat(),
                        'expires_in_seconds': expires_in
                    }
                )
            else:
                logger.error(
                    "Invalid login response: Missing tokens",
                    extra={
                        'event_type': 'slt_api_login_invalid_response',
                        'response_keys': list(data.keys())
                    }
                )
                raise Exception("Invalid login response: Missing tokens")
                
        except requests.exceptions.RequestException as e:
            logger.error(
                "SLT API login failed",
                exc_info=True,
                extra={
                    'event_type': 'slt_api_login_failed',
                    'error': str(e),
                    'status_code': response.status_code if 'response' in locals() else None,
                    'response_text': response.text[:200] if 'response' in locals() else None
                }
            )
            raise Exception(f"Login failed: {str(e)}")

    def _get_headers(self):
        """
        Returns headers for authenticated requests, refreshing the token if necessary.
        """
        # Check if token expired
        if self.access_token and self.token_expiry and datetime.now() >= self.token_expiry:
            logger.info(
                "Access token expired", 
                extra={
                    'event_type': 'slt_api_token_expired',
                    'expiry_time': self.token_expiry.isoformat(),
                    'current_time': datetime.now().isoformat()
                }
            )
            self.refresh_access_token()
            
        # Check if token available
        if not self.access_token:
            logger.error(
                "Access token not available", 
                extra={'event_type': 'slt_api_token_missing'}
            )
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
        request_id = f"{endpoint}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.debug(
            f"Fetching data from {endpoint}", 
            extra={
                'event_type': 'slt_api_request_start',
                'api_endpoint': endpoint,
                'request_id': request_id,
                'params': json.dumps(params) if params else None
            }
        )
        
        for attempt in range(2):  # Allow one retry after token refresh
            try:
                start_time = datetime.now()
                response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log response metadata without sensitive content
                logger.debug(
                    f"Response received from {endpoint}", 
                    extra={
                        'event_type': 'slt_api_response_received',
                        'api_endpoint': endpoint,
                        'request_id': request_id,
                        'status_code': response.status_code,
                        'duration_ms': round(duration_ms, 2),
                        'attempt': attempt + 1
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Log success with minimal data for validation
                logger.info(
                    f"Data successfully fetched from {endpoint}",
                    extra={
                        'event_type': 'slt_api_request_success',
                        'api_endpoint': endpoint,
                        'request_id': request_id,
                        'duration_ms': round(duration_ms, 2),
                        'is_success': data.get('isSuccess', False),
                        'data_size_bytes': len(response.text)
                    }
                )
                return data
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None
                
                # Special handling for 401 on first attempt - refresh token
                if status_code == 401 and attempt == 0:
                    logger.warning(
                        "Authentication failed, refreshing token",
                        extra={
                            'event_type': 'slt_api_auth_retry',
                            'api_endpoint': endpoint,
                            'request_id': request_id,
                            'status_code': status_code,
                            'attempt': attempt + 1
                        }
                    )
                    self.refresh_access_token()
                else:
                    logger.error(
                        f"HTTP error from {endpoint}",
                        exc_info=True,
                        extra={
                            'event_type': 'slt_api_http_error',
                            'api_endpoint': endpoint,
                            'request_id': request_id,
                            'status_code': status_code,
                            'attempt': attempt + 1,
                            'error': str(e),
                            'response_text': e.response.text[:200] if hasattr(e, 'response') else None
                        }
                    )
                    raise Exception(f"Failed to fetch data from {endpoint}: {str(e)}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Request exception for {endpoint}",
                    exc_info=True,
                    extra={
                        'event_type': 'slt_api_request_error',
                        'api_endpoint': endpoint,
                        'request_id': request_id,
                        'attempt': attempt + 1,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                if attempt == 1:  # Only raise if this is the second attempt
                    raise Exception(f"Failed to fetch data from {endpoint}: {str(e)}")

        # Should only reach here if all attempts fail without raising an exception
        logger.error(
            f"All attempts to fetch data from {endpoint} failed",
            extra={
                'event_type': 'slt_api_all_attempts_failed',
                'api_endpoint': endpoint,
                'request_id': request_id
            }
        )
        raise Exception(f"Failed to fetch data from {endpoint} after retries.")

    def refresh_access_token(self):
        """
        Refreshes the access token using the refresh token.
        """
        if not self.refresh_token:
            logger.error(
                "Refresh token not available", 
                extra={'event_type': 'slt_api_refresh_token_missing'}
            )
            raise Exception("Refresh token not available. Please log in first.")

        url = f"{self.BASE_URL}Account/RefreshToken"
        headers = {
            "x-ibm-client-id": self.CLIENT_ID,
            "Content-Type": "application/json",
        }
        payload = {"refreshToken": self.refresh_token}
        
        logger.info(
            "Refreshing access token", 
            extra={'event_type': 'slt_api_token_refresh_attempt'}
        )

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "accessToken" in data:
                self.access_token = data.get("accessToken")
                expires_in = data.get("expiresIn", 3600)  # Default expiry to 1 hour
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(
                    "Access token refreshed successfully", 
                    extra={
                        'event_type': 'slt_api_token_refresh_success',
                        'token_expiry': self.token_expiry.isoformat(),
                        'expires_in_seconds': expires_in
                    }
                )
            else:
                logger.error(
                    "Invalid token refresh response",
                    extra={
                        'event_type': 'slt_api_token_refresh_invalid',
                        'response_keys': list(data.keys())
                    }
                )
                raise Exception("Invalid token refresh response: Missing accessToken")
                
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to refresh token",
                exc_info=True,
                extra={
                    'event_type': 'slt_api_token_refresh_failed',
                    'error': str(e),
                    'status_code': response.status_code if 'response' in locals() else None,
                    'response_text': response.text[:200] if 'response' in locals() else None
                }
            )
            raise Exception(f"Failed to refresh token: {str(e)}")


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
