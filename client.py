import requests

class BinanceTestnetClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def get_server_time(self) -> int:
        """Fetches the current server time from Binance Futures Testnet."""
        url = f"{self.BASE_URL}/fapi/v1/time"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # serverTime is returned as a millisecond timestamp
                server_time = response.json()["serverTime"]
                return server_time
            else:
                raise Exception(f"Failed to fetch time. HTTP Status: {response.status_code}")
        except Exception as e:
            raise Exception(f"Error connecting to Binance: {e}")
