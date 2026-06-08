# Simplified Binance Futures Testnet Trading Bot

A robust and interactive Command Line Interface (CLI) Python application to place Market and Limit orders on the **Binance Futures Testnet (USDT-M)**. It features structured code, comprehensive logging of requests and responses, input validation, and an interactive menu.

---

## Features

- **Order Types:** Supports both `MARKET` and `LIMIT` orders.
- **Order Sides:** Supports both `BUY` and `SELL` sides.
- **Dual CLI Modes:** 
  1. **Interactive Menu:** A user-friendly, prompt-guided interface powered by `questionary` (complete with inline validations and confirmation steps).
  2. **Script Arguments:** Standard argparse-based non-interactive executions for automation.
- **Secure Authentication:** Direct REST API interactions with HMAC-SHA256 request signing using the user's API Secret.
- **Time Synchronization:** Fetches Binance server time dynamically on startup to calculate drift, avoiding timestamp validation errors (`-1021: Timestamp for this request is outside of the recvWindow`).
- **Structured Logging:** Details of API requests, responses, and errors are saved to `trading_bot.log` with a custom formatter. Success/failure summaries are printed cleanly to the console.
- **Robust Validation:** Thorough client-side checks for symbols, quantities, sides, and prices before hitting the API.

---

## Directory Structure

```
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py          # REST Client, request signing, server time sync
│   ├── orders.py          # Coordinates validation and order submission
│   ├── validators.py      # Inputs validation layer (symbol, quantity, price, etc.)
│   └── logging_config.py  # Dual handler logging setup (console & file)
│
├── cli.py                 # Core CLI entry point (Interactive & Arguments mode)
├── requirements.txt       # Project dependencies
└── README.md              # Setup and execution documentation
```

---

## Setup Instructions

### 1. Prerequisites
Ensure you have **Python 3.8 or higher** installed.

### 2. Clone/Extract & Open Folder
Go to the project directory:
```bash
cd trading_bot
```

### 3. Create a Virtual Environment
It is highly recommended to use a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install the required external libraries:
```bash
pip install -r requirements.txt
```

### 5. API Key Configuration
Create a `.env` file in the root folder of `trading_bot/` and enter your Binance Futures Testnet credentials:
```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_key_here
```
> **Tip:** If you run the script in **Interactive Mode** without a `.env` file, the bot will prompt you for your credentials and offer to save them automatically for you!

---

## Usage Examples

### Mode A: Interactive Menu (Recommended)
Simply run the script with no arguments. The bot will guide you through the process step-by-step:
```bash
python cli.py
```

### Mode B: Command Line Arguments
You can also run commands directly by providing parameters:

#### Place a MARKET BUY Order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

#### Place a LIMIT SELL Order:
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 3500.50
```

---

## Logging
- All API request query strings, raw API responses, parameters, network events, and internal logs are appended to **`trading_bot.log`**.
- Format in log file:
  `[timestamp] LEVEL [filename:line]: message`
- Clean summaries are printed directly to the console standard output.

---

## Assumptions & Design Choices
1. **Direct REST Implementation:** Instead of relying on a heavyweight third-party wrapper (like `python-binance`), we built a direct requests-based client. This avoids wrapper deprecation bugs and demonstrates clean API signing logic (HMAC-SHA256).
2. **Server Time Sync:** We calculate the difference between the local machine time and Binance's servers during initialization. This offset is added to all request timestamps, preventing the common `Timestamp for this request is outside of the recvWindow` error caused by local system clock drift.
3. **Safety Confirmations:** In interactive mode, a confirmation prompt shows the final order details before sending the payload, acting as a safeguard for traders.
