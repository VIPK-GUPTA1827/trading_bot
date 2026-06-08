import time
import hmac
import hashlib
import requests
import urllib.parse
from bot.logging_config import logger

class BinanceAPIError(Exception):
    """Exception raised for errors returned by the Binance API."""
    def __init__(self, code, message, response=None):
        self.code = code
        self.message = message
        self.response = response
        super().__init__(f"Binance API Error {code}: {message}")

class BinanceTestnetClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
        # Configure headers
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
        })
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            
        self.time_offset = 0
        # Sync server time on init to avoid clock drift issues
        self.sync_server_time()

    def sync_server_time(self):
        """Fetches the server time and calculates offset from local time to prevent timestamp errors."""
        url = f"{self.BASE_URL}/fapi/v1/time"
        try:
            logger.debug(f"Syncing server time from {url}")
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                server_time = response.json()["serverTime"]
                local_time = int(time.time() * 1000)
                self.time_offset = server_time - local_time
                logger.debug(f"Server time synced. Offset: {self.time_offset}ms")
            else:
                logger.warning(f"Could not sync server time. Status: {response.status_code}. Using local time.")
        except Exception as e:
            logger.warning(f"Error syncing server time: {e}. Using local time.")

    def _get_timestamp(self) -> int:
        """Returns adjusted epoch time in milliseconds."""
        return int(time.time() * 1000) + self.time_offset

    def _sign_payload(self, params: dict) -> str:
        """Generates HMAC-SHA256 signature for the given parameters."""
        if not self.api_secret:
            raise ValueError("API Secret is required to sign requests.")
        
        # Order parameters by key or format them directly
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def send_signed_request(self, method: str, endpoint: str, params: dict) -> dict:
        """Sends an authenticated/signed request to the Binance Futures Testnet API."""
        if not self.api_key or not self.api_secret:
            raise ValueError("Both API Key and API Secret must be set for signed requests.")

        url = f"{self.BASE_URL}{endpoint}"
        
        # Add timestamp and optional recvWindow to parameters
        request_params = params.copy()
        request_params["timestamp"] = self._get_timestamp()
        request_params["recvWindow"] = 60000  # Large window to avoid timing issues

        # Sign parameter string
        signature = self._sign_payload(request_params)
        request_params["signature"] = signature

        logger.debug(f"Sending {method} request to {url}")
        logger.debug(f"Request params (excluding signature/keys): { {k: v for k, v in request_params.items() if k not in ['signature', 'timestamp']} }")

        try:
            if method.upper() == "POST":
                response = self.session.post(url, data=request_params, timeout=15)
            elif method.upper() == "GET":
                response = self.session.get(url, params=request_params, timeout=15)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, data=request_params, timeout=15)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Log the response
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")

            response_json = response.json()
            if response.status_code == 200:
                return response_json
            else:
                # Binance errors usually have code and msg fields
                code = response_json.get("code", -1)
                msg = response_json.get("msg", "Unknown error occurred.")
                raise BinanceAPIError(code, msg, response=response_json)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during API call: {e}")
            raise RuntimeError(f"Network error during API call: {e}")
        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            raise RuntimeError(f"Failed to parse API response as JSON. Response text: {response.text}")
        except BinanceAPIError as e:
            logger.error(f"Binance API returned error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e
