# Binance Futures Testnet Trading Bot

This is a clean, simple Python-based trading bot built for the Binance Futures (USDT-M) Testnet. It supports connection testing, placing MARKET/LIMIT orders, request signing using HMAC-SHA256, and detailed logging of all API payloads.

---

## File Structure

All core project files are located in the root directory:

* `client.py`: Implements the REST Client for Binance Futures, including connection tests, signature generation (HMAC-SHA256), order execution logic, and mock/simulation mode.
* `cli.py`: The command-line entry point which accepts CLI arguments to run tests or execute orders.
* `backtester.py`: An interactive, offline strategy backtester to simulate SMA Crossover or RSI strategies on historical market data (no API keys required).
* `server.py`: FastAPI server script to launch the visual dashboard.
* `index.html`: Modern, glassmorphic dark-mode web dashboard UI.
* `trading_bot.log`: Log file that automatically records all timestamped requests, responses, and errors.
* `requirements.txt`: Project dependencies.
* `README.md`: This documentation.

---

## Setup Instructions

1. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Environment Variables (Optional)**:
    If you want to run real trades, create a `.env` file in the root folder with your Binance Testnet keys:

    ```env
    BINANCE_API_KEY=your_testnet_api_key
    BINANCE_API_SECRET=your_testnet_api_secret
    ```

    *If keys are not provided in `.env`, the bot will automatically fall back to **Mock/Simulation Mode** to safely test execution.*

---

## Usage Examples

* **Launch the Web Dashboard (UI)**:

    ```bash
    python server.py
    ```

    Open `http://localhost:8000` in your web browser.

* **Test API Connection (CLI)**:

    ```bash
    python cli.py --test-connection
    ```

* **Place a Market Order (CLI)**:

    ```bash
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
    ```

* **Place a Limit Order (CLI)**:

    ```bash
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.005 --price 98000
    ```

* **Force Mock Mode** (Simulate without real API keys):

    ```bash
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --mock
    ```

### Mode C: Offline Backtesting

Run the backtester to simulate performance statistics (returns, drawdowns, win rate) of trading strategies on historical data without requiring API keys:

```bash
python backtester.py
```

Follow the prompts to select target trading pair, candlestick interval (15m, 1h, 4h, 1d), strategy types (SMA Crossover / RSI), custom indicators period, and start capital.

---

## Logging

All operations are logged with timestamps in `trading_bot.log`. A sample log contains:

* Connection status checks.
* Request parameters before signature generation.
* HTTP status codes and full response JSON arrays from Binance APIs.
