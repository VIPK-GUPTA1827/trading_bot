import sys
import os
import requests
import time
from datetime import datetime

# Reconfigure stdout/stderr to utf-8 to avoid console encoding crashes with emojis on Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class BinanceBacktester:
    BASE_URL = "https://fapi.binance.com"  # Using live Futures API for historical data

    def __init__(self):
        pass

    def fetch_klines(self, symbol: str, interval: str, limit: int = 1000) -> list:
        """Fetches historical K-lines (candlesticks) from Binance Futures public API."""
        url = f"{self.BASE_URL}/fapi/v1/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        print(Fore.CYAN + f"\nDownloading last {limit} candles for {symbol.upper()} (Interval: {interval})...")
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(Fore.GREEN + f"Successfully downloaded {len(data)} candles.")
                return data
            else:
                print(Fore.RED + f"Failed to download data. Status code: {response.status_code}, Msg: {response.text}")
                return []
        except Exception as e:
            print(Fore.RED + f"Error downloading historical data: {e}")
            return []

    def calculate_sma(self, close_prices: list, period: int) -> list:
        """Calculates Simple Moving Average (SMA) in pure Python."""
        sma = []
        for i in range(len(close_prices)):
            if i < period - 1:
                sma.append(None)
            else:
                sma.append(sum(close_prices[i - period + 1 : i + 1]) / period)
        return sma

    def calculate_rsi(self, close_prices: list, period: int = 14) -> list:
        """Calculates Relative Strength Index (RSI) in pure Python using smoothed Wilder's MA."""
        rsi_values = []
        if len(close_prices) < period + 1:
            return [None] * len(close_prices)
        
        deltas = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
        
        # Calculate initial average gain/loss
        gains = [d if d > 0 else 0 for d in deltas[:period]]
        losses = [-d if d < 0 else 0 for d in deltas[:period]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        rsi_values.extend([None] * period)
        
        if avg_loss == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100.0 - (100.0 / (1.0 + rs)))
            
        # Wilder's Smoothing
        for i in range(period, len(deltas)):
            d = deltas[i]
            gain = d if d > 0 else 0
            loss = -d if d < 0 else 0
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(100.0 - (100.0 / (1.0 + rs)))
                
        return rsi_values

    def run_backtest(self, candles: list, strategy: str, initial_capital: float = 10000.0, **kwargs) -> dict:
        """Runs the trade simulation engine based on historical candles and chosen strategy."""
        if not candles:
            return {}

        # Parse candle data
        timestamps = [c[0] for c in candles]
        close_prices = [float(c[4]) for c in candles]
        high_prices = [float(c[2]) for c in candles]
        low_prices = [float(c[3]) for c in candles]
        
        n_candles = len(close_prices)
        
        # Calculate strategy indicators
        signals = [0] * n_candles  # 1 = BUY, -1 = SELL, 0 = HOLD
        
        if strategy == "SMA_CROSSOVER":
            fast_p = kwargs.get("fast_period", 9)
            slow_p = kwargs.get("slow_period", 21)
            fast_sma = self.calculate_sma(close_prices, fast_p)
            slow_sma = self.calculate_sma(close_prices, slow_p)
            
            for i in range(1, n_candles):
                if fast_sma[i-1] is None or slow_sma[i-1] is None:
                    continue
                # Crossover Buy: Fast crosses above Slow
                if fast_sma[i-1] <= slow_sma[i-1] and fast_sma[i] > slow_sma[i]:
                    signals[i] = 1
                # Crossunder Sell: Fast crosses below Slow
                elif fast_sma[i-1] >= slow_sma[i-1] and fast_sma[i] < slow_sma[i]:
                    signals[i] = -1
                    
        elif strategy == "RSI":
            rsi_period = kwargs.get("rsi_period", 14)
            oversold = kwargs.get("rsi_oversold", 30)
            overbought = kwargs.get("rsi_overbought", 70)
            rsi = self.calculate_rsi(close_prices, rsi_period)
            
            for i in range(1, n_candles):
                if rsi[i-1] is None or rsi[i] is None:
                    continue
                # Buy when RSI dips below oversold threshold
                if rsi[i-1] >= oversold > rsi[i]:
                    signals[i] = 1
                # Sell when RSI rises above overbought threshold
                elif rsi[i-1] <= overbought < rsi[i]:
                    signals[i] = -1

        # Trade Simulation Variables
        capital = initial_capital
        position = 0.0
        in_position = False
        entry_price = 0.0
        trades = []
        portfolio_history = []
        trading_fee_pct = 0.0004  # 0.04% standard maker/taker fee
        
        peak_portfolio_val = initial_capital
        max_drawdown = 0.0

        for i in range(n_candles):
            current_price = close_prices[i]
            current_time = datetime.fromtimestamp(timestamps[i] / 1000).strftime('%Y-%m-%d %H:%M')
            
            # Execute Sell
            if in_position and signals[i] == -1:
                revenue = position * current_price
                fee = revenue * trading_fee_pct
                net_revenue = revenue - fee
                capital = net_revenue
                
                profit = capital - (position * entry_price)
                return_pct = (current_price - entry_price) / entry_price * 100
                
                trades.append({
                    "type": "SELL",
                    "price": current_price,
                    "time": current_time,
                    "profit": profit,
                    "return_pct": return_pct,
                    "balance": capital
                })
                
                position = 0.0
                in_position = False
                
            # Execute Buy
            elif not in_position and signals[i] == 1:
                fee = capital * trading_fee_pct
                net_capital = capital - fee
                position = net_capital / current_price
                entry_price = current_price
                in_position = True
                
                trades.append({
                    "type": "BUY",
                    "price": current_price,
                    "time": current_time,
                    "balance": capital
                })

            # Calculate current portfolio value
            current_portfolio_val = capital if not in_position else (position * current_price)
            portfolio_history.append(current_portfolio_val)
            
            # Peak and Drawdown tracking
            if current_portfolio_val > peak_portfolio_val:
                peak_portfolio_val = current_portfolio_val
            
            drawdown = (peak_portfolio_val - current_portfolio_val) / peak_portfolio_val * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Force exit last position if still holding at the end to calculate final stats
        if in_position:
            current_price = close_prices[-1]
            current_time = datetime.fromtimestamp(timestamps[-1] / 1000).strftime('%Y-%m-%d %H:%M')
            revenue = position * current_price
            fee = revenue * trading_fee_pct
            capital = revenue - fee
            
            profit = capital - (position * entry_price)
            return_pct = (current_price - entry_price) / entry_price * 100
            
            trades.append({
                "type": "SELL (EXIT)",
                "price": current_price,
                "time": current_time,
                "profit": profit,
                "return_pct": return_pct,
                "balance": capital
            })
            
        # Performance Summary Calculation
        final_value = capital
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        # Buy & Hold Return
        bh_return = (close_prices[-1] - close_prices[0]) / close_prices[0] * 100
        
        # Trade statistics
        sell_trades = [t for t in trades if "SELL" in t["type"]]
        total_trades = len(sell_trades)
        winning_trades = len([t for t in sell_trades if t["profit"] > 0])
        losing_trades = len([t for t in sell_trades if t["profit"] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "bh_return": bh_return,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "trade_logs": trades
        }

    def display_results(self, results: dict, symbol: str, interval: str, strategy: str):
        """Displays formatted simulation results using colorama styling."""
        if not results:
            print(Fore.RED + "No results to display. Backtest might have failed.")
            return

        print("\n" + "=" * 55)
        print(Style.BRIGHT + Fore.GREEN + f" 📊 BACKTEST PERFORMANCE REPORT: {symbol.upper()} ({interval}) ")
        print("=" * 55)
        
        strategy_name = "SMA Crossover" if strategy == "SMA_CROSSOVER" else "RSI Strategy"
        print(f"Strategy Run      :  {Fore.YELLOW}{strategy_name}")
        print(f"Initial Capital   :  ${results['initial_capital']:.2f} USDT")
        
        final_color = Fore.GREEN if results['final_value'] >= results['initial_capital'] else Fore.RED
        print(f"Final Capital     :  {final_color}${results['final_value']:.2f} USDT")
        
        return_color = Fore.GREEN if results['total_return'] >= 0 else Fore.RED
        print(f"Strategy Return   :  {return_color}{results['total_return']:.2f}%")
        
        bh_color = Fore.GREEN if results['bh_return'] >= 0 else Fore.RED
        print(f"Buy & Hold Return :  {bh_color}{results['bh_return']:.2f}%")
        
        # Outperformance check
        diff = results['total_return'] - results['bh_return']
        diff_color = Fore.GREEN if diff >= 0 else Fore.RED
        print(f"Outperformance    :  {diff_color}{diff:+.2f}% vs Buy & Hold")
        
        print("-" * 55)
        print(f"Total Closed Trades:  {results['total_trades']}")
        print(f"Winning Trades    :  {Fore.GREEN}{results['winning_trades']}")
        print(f"Losing Trades     :  {Fore.RED}{results['losing_trades']}")
        
        win_rate_color = Fore.GREEN if results['win_rate'] >= 50 else Fore.YELLOW
        print(f"Win Rate          :  {win_rate_color}{results['win_rate']:.1f}%")
        print(f"Max Portfolio DD  :  {Fore.RED}{results['max_drawdown']:.2f}%")
        print("=" * 55)

        # Prompt to print detailed logs
        show_logs = confirm_option("Do you want to see the detailed transaction logs?")
        if show_logs:
            print("\n" + Style.BRIGHT + Fore.CYAN + "📜 TRANSACTION LOGS:")
            print("-" * 75)
            print(f"{'Time':<18} | {'Type':<10} | {'Price':<12} | {'Profit ($)':<12} | {'Return (%)':<10} | {'Balance ($)':<12}")
            print("-" * 75)
            
            for t in results["trade_logs"]:
                t_type = t["type"]
                price = f"${t['price']:.2f}"
                balance = f"${t['balance']:.2f}"
                
                if "BUY" in t_type:
                    type_str = Fore.GREEN + t_type
                    profit_str = "-"
                    ret_str = "-"
                else:
                    type_str = Fore.RED + t_type
                    p_color = Fore.GREEN if t['profit'] > 0 else Fore.RED
                    profit_str = p_color + f"{t['profit']:+.2f}"
                    ret_str = p_color + f"{t['return_pct']:+.2f}%"
                    
                print(f"{t['time']:<18} | {type_str:<19} | {price:<12} | {profit_str:<21} | {ret_str:<19} | {balance:<12}")
            print("-" * 75)

# Input utility helpers
def select_option(title: str, choices: list) -> str:
    print(Style.BRIGHT + Fore.CYAN + f"\n{title}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    while True:
        try:
            val = input(f"Select option (1-{len(choices)}): ").strip()
            idx = int(val) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(Fore.RED + f"Invalid input. Please enter a number between 1 and {len(choices)}.")

def confirm_option(title: str) -> bool:
    while True:
        val = input(f"\n{title} (y/n): ").strip().lower()
        if val in ['y', 'yes']:
            return True
        elif val in ['n', 'no']:
            return False
        print(Fore.RED + "Please enter 'y' or 'n'.")

def get_text_input(prompt: str, default: str = "") -> str:
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default

def main():
    print(Style.BRIGHT + Fore.CYAN + "=" * 55)
    print(Style.BRIGHT + Fore.CYAN + "   ⚙️   ALGORITHMIC TRADING BOT BACKTESTER   ⚙️   ")
    print(Style.BRIGHT + Fore.CYAN + "=" * 55)

    backtester = BinanceBacktester()

    # 1. Choose Pair
    symbol = select_option(
        "Select Trading Pair to Backtest:",
        ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    )

    # 2. Choose Interval
    interval = select_option(
        "Select Candlestick Interval:",
        ["15m", "1h", "4h", "1d"]
    )

    # 3. Select Strategy
    strategy = select_option(
        "Select Trading Strategy:",
        [
            "SMA Crossover (Fast SMA vs Slow SMA)",
            "RSI Strategy (Oversold Buy, Overbought Sell)"
        ]
    )

    # 4. Set parameters
    kwargs = {}
    if "SMA" in strategy:
        strategy_code = "SMA_CROSSOVER"
        fast_sma = get_text_input("Enter Fast SMA period", default="9")
        slow_sma = get_text_input("Enter Slow SMA period", default="21")
        kwargs["fast_period"] = int(fast_sma) if fast_sma.isdigit() else 9
        kwargs["slow_period"] = int(slow_sma) if slow_sma.isdigit() else 21
    else:
        strategy_code = "RSI"
        rsi_period = get_text_input("Enter RSI period", default="14")
        rsi_oversold = get_text_input("Enter RSI Oversold Threshold (Buy)", default="30")
        rsi_overbought = get_text_input("Enter RSI Overbought Threshold (Sell)", default="70")
        kwargs["rsi_period"] = int(rsi_period) if rsi_period.isdigit() else 14
        kwargs["rsi_oversold"] = int(rsi_oversold) if rsi_oversold.isdigit() else 30
        kwargs["rsi_overbought"] = int(rsi_overbought) if rsi_overbought.isdigit() else 70

    initial_capital_str = get_text_input("Enter Initial Capital (USDT)", default="10000")
    try:
        capital = float(initial_capital_str)
    except ValueError:
        capital = 10000.0

    # 5. Run it
    candles = backtester.fetch_klines(symbol, interval, limit=1000)
    
    if not candles:
        print(Fore.RED + "Error: No candlestick data retrieved. Exiting backtester.")
        sys.exit(1)

    results = backtester.run_backtest(candles, strategy_code, initial_capital=capital, **kwargs)
    backtester.display_results(results, symbol, interval, strategy_code)

if __name__ == "__main__":
    main()
