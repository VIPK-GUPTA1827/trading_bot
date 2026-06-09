import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class BinanceTestnetClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self):
        # API credentials fetch karenge .env file ya environment variables se
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")

    def get_server_time(self) -> int:
        """Fetches the current server time from Binance Futures Testnet."""
        url = f"{self.BASE_URL}/fapi/v1/time"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Millisecond server time return karega
                return response.json()["serverTime"]
            else:
                raise Exception(f"Failed to fetch time. HTTP Status: {response.status_code}")
        except Exception as e:
            raise Exception(f"Error connecting to Binance: {e}")

    def generate_signature(self, query_string: str) -> str:
        """Generates HMAC-SHA256 signature using the API Secret."""
        if not self.api_secret:
            raise Exception("API Secret is missing in environment. Cannot generate signature.")
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, mock: bool = False):
        """Places a MARKET or LIMIT order. Automatically falls back to Mock Mode if keys are not present."""
        
        # Agar key ya secret empty hai, ya mock=True pass kiya hai, to simulation mode chalega
        is_mock = mock or not self.api_key or not self.api_secret
        
        log_message(f"Initiating {order_type} {side} order for {quantity} {symbol} (MockMode={is_mock})")

        if is_mock:
            # Mock mode: dummy successful response return karenge
            simulated_order_id = int(time.time() * 1000)
            simulated_price = price if price else 95000.0  # dummy price if market order
            response_data = {
                "orderId": simulated_order_id,
                "symbol": symbol.upper(),
                "status": "FILLED" if order_type.upper() == "MARKET" else "NEW",
                "clientOrderId": f"mock_{simulated_order_id}",
                "price": str(simulated_price),
                "origQty": str(quantity),
                "executedQty": str(quantity) if order_type.upper() == "MARKET" else "0.0",
                "side": side.upper(),
                "type": order_type.upper(),
                "timeInForce": "GTC",
                "updateTime": int(time.time() * 1000)
            }
            log_message(f"MOCK REQUEST: Symbol={symbol}, Side={side}, Type={order_type}, Qty={quantity}, Price={price}")
            log_message(f"MOCK RESPONSE: {response_data}")
            return response_data

        # Real mode order placement
        # 1. Server time retrieve karenge synchronization ke liye
        try:
            server_time = self.get_server_time()
        except Exception as e:
            log_message(f"Warning: Could not sync server time ({e}). Using local time.")
            server_time = int(time.time() * 1000)

        # 2. Parameters dictionary build karenge
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
            "timestamp": server_time,
            "recvWindow": 5000
        }
        
        # Limit order details add karenge
        if order_type.upper() == "LIMIT":
            if not price:
                raise Exception("Price is required for LIMIT orders.")
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        # 3. Query string banakar HMAC-SHA256 signature generate karenge
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self.generate_signature(query_string)
        params["signature"] = signature

        # 4. HTTP POST request send karenge
        url = f"{self.BASE_URL}/fapi/v1/order"
        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        log_message(f"REAL REQUEST: POST {url} with params: {query_string}&signature={signature}")

        try:
            response = requests.post(url, headers=headers, params=params, timeout=15)
            response_json = response.json()
            log_message(f"REAL RESPONSE HTTP {response.status_code}: {response_json}")
            
            if response.status_code == 200:
                return response_json
            else:
                error_msg = response_json.get("msg", "Unknown error")
                error_code = response_json.get("code", "Unknown code")
                raise Exception(f"Binance API Error {error_code}: {error_msg}")
        except Exception as e:
            log_message(f"HTTP Order Request Failed: {e}")
            raise e

def log_message(message: str):
    """Logs a timestamped message to console and trading_bot.log file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_log = f"[{timestamp}] {message}"
    
    # Console display (clean format without emoji to avoid Windows UnicodeEncodeError)
    print(formatted_log)
    
    # File write operation
    try:
        # Save to trading_bot.log file
        with open("trading_bot.log", "a", encoding="utf-8") as log_file:
            log_file.write(formatted_log + "\n")
    except Exception as e:
        print(f"Log writing failed: {e}")
