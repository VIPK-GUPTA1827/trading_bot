import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from client import BinanceTestnetClient, log_message

app = FastAPI(title="Binance Futures Testnet Dashboard API")
client = BinanceTestnetClient()

class OrderRequest(BaseModel):
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None
    mock: bool = False

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the main dashboard page."""
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Dashboard index.html not found.")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/order")
async def place_order(order: OrderRequest):
    """API Endpoint to place MARKET or LIMIT orders."""
    try:
        result = client.place_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.type,
            quantity=order.quantity,
            price=order.price,
            mock=order.mock
        )
        return {"success": true, "data": result}
    except Exception as e:
        log_message(f"API Error placing order: {e}")
        return JSONResponse(
            status_code=400,
            content={"success": false, "detail": str(e)}
        )

@app.get("/api/logs")
async def get_logs():
    """Returns the last 50 lines of the trading_bot.log file."""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading_bot.log")
    if not os.path.exists(log_path):
        return {"logs": ["[System] No logs recorded yet."]}
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Last 50 lines return karenge
        last_lines = [line.strip() for line in lines[-50:]]
        return {"logs": last_lines}
    except Exception as e:
        return {"logs": [f"[System] Error reading log file: {e}"]}

# JS/JSON compatibility fix
true = True
false = False

if __name__ == "__main__":
    print("Starting server on http://localhost:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
