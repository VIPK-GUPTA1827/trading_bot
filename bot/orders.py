from bot.client import BinanceTestnetClient, BinanceAPIError
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price
)
from bot.logging_config import logger

class OrderManager:
    def __init__(self, client: BinanceTestnetClient):
        self.client = client

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> dict:
        """
        Validates order parameters and submits a signed order request to the Binance Futures Testnet.
        """
        # Validate inputs
        val_symbol = validate_symbol(symbol)
        val_side = validate_side(side)
        val_type = validate_order_type(order_type)
        val_qty = validate_quantity(quantity)
        val_price = validate_price(price, val_type)

        # Prepare request parameters
        params = {
            "symbol": val_symbol,
            "side": val_side,
            "type": val_type,
            "quantity": str(val_qty),
        }

        # LIMIT orders require price and timeInForce
        if val_type == "LIMIT":
            params["price"] = str(val_price)
            params["timeInForce"] = "GTC"  # Good 'til Cancelled

        # Log order request summary
        logger.info(f"Preparing order: {val_type} {val_side} {val_qty} {val_symbol}" + 
                    (f" @ {val_price}" if val_type == "LIMIT" else ""))

        try:
            # Send signed request to place order
            response = self.client.send_signed_request("POST", "/fapi/v1/order", params)
            
            # Print and log success
            order_id = response.get("orderId")
            status = response.get("status")
            executed_qty = response.get("executedQty", "0.0")
            avg_price = response.get("avgPrice", "0.0")
            
            logger.info(f"Order Placed Successfully! Order ID: {order_id}, Status: {status}")
            
            return {
                "success": True,
                "orderId": order_id,
                "status": status,
                "executedQty": executed_qty,
                "avgPrice": avg_price,
                "response": response
            }

        except BinanceAPIError as e:
            logger.error(f"Failed to place order. API Code: {e.code}, Message: {e.message}")
            return {
                "success": False,
                "error": f"API Error {e.code}: {e.message}",
                "response": e.response
            }
        except Exception as e:
            logger.error(f"Failed to place order due to unexpected error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
