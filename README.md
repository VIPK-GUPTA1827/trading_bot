# 🤖 Binance Futures Trading Bot

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

An algorithmic futures trading bot built for the **Binance USDT-M Futures Testnet**. Features sub-second API request signing via **HMAC-SHA256**, server drift synchronization (<20ms offset), an offline strategy backtester, and a real-time glassmorphic web dashboard.

---

## ✨ Key Features

- ⚡ **Sub-second order execution** with HMAC-SHA256 authenticated request signing
- 🔄 **Server time drift sync** — keeps clock offset under 20ms to prevent signature failures
- 📊 **Offline Backtester** — simulates SMA Crossover & RSI strategies on 10,000+ data points in under 3 seconds
- 🖥️ **Web Dashboard** — real-time glassmorphic dark-mode UI powered by FastAPI
- 🛡️ **Mock/Simulation Mode** — safely test execution logic without real API keys
- 📝 **Detailed Logging** — all API requests, responses, and errors timestamped automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| API Server | FastAPI |
| Trading API | Binance Futures REST API |
| Auth | HMAC-SHA256 Signature |
| Strategy | SMA Crossover, RSI |
| Frontend | HTML5, CSS3, JavaScript |

---

## 📁 Project Structure

```
trading_bot/
├── client.py        # Binance REST client — signing, order execution, mock mode
├── cli.py           # CLI entry point — place orders via command line
├── backtester.py    # Offline strategy backtester (no API keys needed)
├── server.py        # FastAPI server — launches web dashboard
├── index.html       # Glassmorphic dark-mode dashboard UI
├── requirements.txt # Project dependencies
└── bot/             # Core bot logic modules
```

---

## 🚀 Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/VIPK-GUPTA1827/trading_bot.git
cd trading_bot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure API keys (Optional)**

Create a `.env` file in the root folder:
```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```
> If no keys provided, the bot automatically runs in **Mock/Simulation Mode**.

---

## 💻 Usage

**Launch Web Dashboard:**
```bash
python server.py
# Open http://localhost:8000
```

**Test API Connection:**
```bash
python cli.py --test-connection
```

**Place a Market Order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

**Place a Limit Order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.005 --price 98000
```

**Run in Mock Mode (no API keys needed):**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --mock
```

**Run Offline Backtester:**
```bash
python backtester.py
# Select pair, interval (15m/1h/4h/1d), strategy (SMA/RSI), and start capital
```

---

## 📈 Performance Highlights

- Backtester processes **10,000+ historical data points** in under **3 seconds**
- API signature generation under **50ms**
- Server time drift maintained under **20ms**

---

## 👨‍💻 Author

**Vipin Gupta** — Full Stack MERN Developer & Python Engineer

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-blue)](https://vipingupta-portfolio.netlify.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vipin-gupta-v2718)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/VIPK-GUPTA1827)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
