import re

def validate_symbol(symbol: str) -> str:
    """Validates and formats trading symbol (e.g., BTCUSDT)."""
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    
    clean_symbol = symbol.strip().upper()
    # Simple regex to ensure it's alphanumeric and typically ends with USDT/BUSD/USDC etc.
    if not re.match(r"^[A-Z0-9]{3,15}$", clean_symbol):
        raise ValueError(f"Invalid symbol format: '{symbol}'. Must be alphanumeric (e.g. BTCUSDT).")
    
    return clean_symbol

def validate_side(side: str) -> str:
    """Validates order side (BUY/SELL)."""
    if not side:
        raise ValueError("Side cannot be empty.")
    
    clean_side = side.strip().upper()
    if clean_side not in ["BUY", "SELL"]:
        raise ValueError(f"Invalid side: '{side}'. Must be either 'BUY' or 'SELL'.")
    
    return clean_side

def validate_order_type(order_type: str) -> str:
    """Validates order type (MARKET/LIMIT)."""
    if not order_type:
        raise ValueError("Order type cannot be empty.")
    
    clean_type = order_type.strip().upper()
    if clean_type not in ["MARKET", "LIMIT"]:
        raise ValueError(f"Invalid order type: '{order_type}'. Must be either 'MARKET' or 'LIMIT'.")
    
    return clean_type

def validate_quantity(quantity) -> float:
    """Validates order quantity is a positive float."""
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity: '{quantity}'. Must be a number.")
        
    if qty_float <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty_float}")
        
    return qty_float

def validate_price(price, order_type: str):
    """Validates order price is a positive float for LIMIT orders."""
    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price: '{price}'. Must be a number.")
            
        if price_float <= 0:
            raise ValueError(f"Price must be greater than 0. Got: {price_float}")
        return price_float
    return None
