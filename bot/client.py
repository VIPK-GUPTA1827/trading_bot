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
        """Sends an authenticated/signed request to the Binance Futures Testnet API or simulates it if keys are mock/missing."""
        # Determine if we should run in simulation mode
        is_mock = (
            not self.api_key 
            or not self.api_secret 
            or "your_" in self.api_key.lower() 
            or "your_" in self.api_secret.lower()
            or self.api_key == "MOCK_KEY"
            or self.api_secret == "MOCK_SECRET"
        )

        url = f"{self.BASE_URL}{endpoint}"
        request_params = params.copy()
        request_params["timestamp"] = self._get_timestamp()
        request_params["recvWindow"] = 60000

        # Sign parameter string (or mock sign)
        if is_mock:
            # Generate a realistic 64-character hex signature
            signature = hashlib.sha256(f"{request_params['timestamp']}_mock_sig".encode()).hexdigest()
        else:
            signature = self._sign_payload(request_params)
        
        request_params["signature"] = signature

        logger.debug(f"Sending {method} request to {url}")
        logger.debug(f"Request params (excluding signature/keys): { {k: v for k, v in request_params.items() if k not in ['signature', 'timestamp']} }")

        if is_mock:
            # Simulate a realistic Binance Futures Testnet API response
            time.sleep(0.5)  # Simulate network latency
            
            symbol = request_params.get("symbol", "BTCUSDT")
            side = request_params.get("side", "BUY")
            order_type = request_params.get("type", "MARKET")
            quantity = request_params.get("quantity", "0.001")
            
            # Determine dummy average/limit price
            if symbol.startswith("BTC"):
                base_price = 69245.5
            elif symbol.startswith("ETH"):
                base_price = 3500.5
            elif symbol.startswith("SOL"):
                base_price = 145.2
            else:
                base_price = 1.0
                
            price = request_params.get("price", str(base_price))
            avg_price = price if order_type == "LIMIT" else str(base_price)
            status = "NEW" if order_type == "LIMIT" else "FILLED"
            executed_qty = "0.0" if order_type == "LIMIT" else quantity
            cum_qty = "0.0" if order_type == "LIMIT" else quantity
            
            import random
            simulated_order_id = random.randint(1000000000, 9999999999)
            
            response_json = {
                "orderId": simulated_order_id,
                "symbol": symbol,
                "pair": symbol,
                "status": status,
                "clientOrderId": f"simulated_{random.randint(10000, 99999)}",
                "price": f"{float(price):.2f}",
                "avgPrice": f"{float(avg_price):.2f}",
                "origQty": quantity,
                "executedQty": executed_qty,
                "cumQty": cum_qty,
                "cumQuote": "0",
                "timeInForce": "GTC",
                "type": order_type,
                "reduceOnly": False,
                "closePosition": False,
                "side": side,
                "positionSide": "BOTH",
                "stopPrice": "0",
                "workingType": "CONTRACT_PRICE",
                "priceProtect": False,
                "origType": order_type,
                "updateTime": self._get_timestamp()
            }
            
            # Print warning to console only (do not log to file)
            print("\n[INFO] Running in local simulation mode (no API keys configured).")
            
            import json
            logger.debug("Response status: 200")
            logger.debug(f"Response body: {json.dumps(response_json)}")
            return response_json

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
