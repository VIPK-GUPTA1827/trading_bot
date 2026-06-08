import os
import sys

# Reconfigure stdout/stderr to utf-8 to avoid console encoding crashes with emojis on Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
from dotenv import load_dotenv, set_key
import questionary
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add parent directory to path so bot package can be imported if run directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging, logger
from bot.client import BinanceTestnetClient
from bot.orders import OrderManager

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

def load_credentials():
    """Loads API key and secret from environment or .env file."""
    if os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
    return os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET")

def setup_env_credentials(api_key, api_secret):
    """Saves API credentials to .env file."""
    set_key(ENV_FILE, "BINANCE_API_KEY", api_key)
    set_key(ENV_FILE, "BINANCE_API_SECRET", api_secret)
    print(Fore.GREEN + f"Credentials successfully saved to {ENV_FILE}")

def run_interactive_menu():
    """Runs a beautiful interactive CLI questionnaire to configure and place orders."""
    print(Style.BRIGHT + Fore.CYAN + "=" * 55)
    print(Style.BRIGHT + Fore.CYAN + "   🚀 BINANCE FUTURES TESTNET TRADING BOT 🚀   ")
    print(Style.BRIGHT + Fore.CYAN + "=" * 55)

    api_key, api_secret = load_credentials()

    # If credentials are missing, guide the user to enter them or run in simulation mode
    if not api_key or not api_secret:
        print(Fore.YELLOW + "API credentials not found in environment or .env file.")
        action_choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Run in Simulation Mode (No API keys required, simulated execution)",
                "Configure API credentials now (Enter API Key and Secret)",
                "Exit"
            ]
        ).ask()
        
        if action_choice == "Exit" or action_choice is None:
            print(Fore.RED + "Exiting...")
            sys.exit(0)
            
        elif action_choice == "Run in Simulation Mode (No API keys required, simulated execution)":
            api_key = "MOCK_KEY"
            api_secret = "MOCK_SECRET"
            print(Fore.GREEN + "Starting in SIMULATION MODE. Orders will be simulated locally.")
            
        else:
            api_key = questionary.text("Enter your Binance Futures Testnet API Key:").ask()
            api_secret = questionary.password("Enter your Binance Futures Testnet Secret Key:").ask()
            
            if not api_key or not api_secret:
                print(Fore.RED + "API Key and Secret cannot be empty.")
                sys.exit(1)
                
            save_env = questionary.confirm("Save these credentials to .env file?").ask()
            if save_env:
                setup_env_credentials(api_key, api_secret)
                # Reload dotenv to set environment variables
                load_dotenv(ENV_FILE)

    # Initialize client and manager
    try:
        client = BinanceTestnetClient(api_key=api_key, api_secret=api_secret)
        manager = OrderManager(client)
    except Exception as e:
        print(Fore.RED + f"Error initializing Binance client: {e}")
        sys.exit(1)

    # 1. Symbol selection
    symbol_choice = questionary.select(
        "Select Trading Pair:",
        choices=[
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "XRPUSDT",
            "Enter custom pair..."
        ]
    ).ask()

    if symbol_choice == "Enter custom pair...":
        symbol = questionary.text("Enter Symbol (e.g., DOGEUSDT):").ask()
    else:
        symbol = symbol_choice

    if not symbol:
        print(Fore.RED + "Symbol cannot be empty.")
        sys.exit(1)

    # 2. Side selection
    side = questionary.select(
        "Select Order Side:",
        choices=["BUY", "SELL"]
    ).ask()

    # 3. Order Type selection
    order_type = questionary.select(
        "Select Order Type:",
        choices=["MARKET", "LIMIT"]
    ).ask()

    # 4. Quantity input with inline validation helper
    def is_valid_qty(val):
        try:
            return float(val) > 0
        except ValueError:
            return False

    qty_text = questionary.text(
        "Enter Quantity (e.g., 0.001):",
        validate=lambda val: True if is_valid_qty(val) else "Quantity must be a positive number."
    ).ask()
    quantity = float(qty_text)

    # 5. Price input (only for LIMIT orders)
    price = None
    if order_type == "LIMIT":
        def is_valid_price(val):
            try:
                return float(val) > 0
            except ValueError:
                return False
        
        price_text = questionary.text(
            "Enter Limit Price (e.g., 65000):",
            validate=lambda val: True if is_valid_price(val) else "Price must be a positive number."
        ).ask()
        price = float(price_text)

    # 6. Confirm Order Placement
    order_summary_str = f"{Fore.GREEN if side == 'BUY' else Fore.RED}{side}{Style.RESET_ALL} {order_type} order of {Fore.YELLOW}{quantity} {symbol}"
    if price:
        order_summary_str += f" @ {Fore.YELLOW}{price} USDT"

    print(f"\nOrder Summary: {order_summary_str}")
    confirm_place = questionary.confirm("Do you want to submit this order?").ask()

    if not confirm_place:
        print(Fore.YELLOW + "Order placement cancelled.")
        sys.exit(0)

    # Place order
    print(Fore.CYAN + "Submitting order to Binance Futures Testnet...")
    result = manager.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price
    )

    print_order_result(result)


def run_args_mode(args):
    """Executes order placement using command-line arguments."""
    api_key, api_secret = load_credentials()
    
    if not api_key or not api_secret:
        print(Fore.YELLOW + "API credentials not found. Falling back to Simulation Mode (MOCK).")
        api_key = "MOCK_KEY"
        api_secret = "MOCK_SECRET"

    try:
        client = BinanceTestnetClient(api_key=api_key, api_secret=api_secret)
        manager = OrderManager(client)
    except Exception as e:
        print(Fore.RED + f"Error initializing Binance client: {e}")
        sys.exit(1)

    print(Fore.CYAN + f"Submitting command line order to Binance Futures Testnet...")
    result = manager.place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=args.price
    )

    print_order_result(result)


def print_order_result(result: dict):
    """Prints a beautiful summary of the order outcome."""
    print(Style.BRIGHT + Fore.CYAN + "\n" + "=" * 55)
    if result["success"]:
        print(Style.BRIGHT + Fore.GREEN + "   🎉 ORDER PLACED SUCCESSFULLY 🎉   ")
        print(Style.BRIGHT + Fore.CYAN + "=" * 55)
        print(f"{Fore.WHITE}Order ID:        {Fore.YELLOW}{result['orderId']}")
        print(f"{Fore.WHITE}Status:          {Fore.GREEN}{result['status']}")
        print(f"{Fore.WHITE}Executed Qty:    {Fore.YELLOW}{result['executedQty']}")
        print(f"{Fore.WHITE}Avg Price:       {Fore.YELLOW}{result['avgPrice']} USDT")
        print(Fore.GREEN + "\nAPI response and details have been logged to 'trading_bot.log'.")
    else:
        print(Style.BRIGHT + Fore.RED + "   ❌ ORDER PLACEMENT FAILED ❌   ")
        print(Style.BRIGHT + Fore.CYAN + "=" * 55)
        print(f"{Fore.RED}Error Details:   {result['error']}")
        print(Fore.RED + "\nFailure details have been logged to 'trading_bot.log'.")
    print(Style.BRIGHT + Fore.CYAN + "=" * 55)


if __name__ == "__main__":
    # Initialize logging
    setup_logging()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Place Market or Limit orders on Binance Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in interactive mode:
  python cli.py
  
  # Run in command line mode:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
        """
    )
    
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT"], help="Order type")
    parser.add_argument("--quantity", type=float, help="Quantity to trade")
    parser.add_argument("--price", type=float, help="Price (required for LIMIT orders)")
    parser.add_argument("--interactive", action="store_true", help="Force interactive prompts mode")

    args = parser.parse_args()

    # If any specific trading argument is provided, run in command line mode
    # unless --interactive is explicitly passed.
    has_trade_args = any([args.symbol, args.side, args.type, args.quantity])
    
    if args.interactive or not has_trade_args:
        run_interactive_menu()
    else:
        # Check command line parameter requirements
        if not args.symbol or not args.side or not args.type or not args.quantity:
            print(Fore.RED + "Error: When running in non-interactive mode, all of --symbol, --side, --type, and --quantity are required.")
            parser.print_help()
            sys.exit(1)
        if args.type.upper() == "LIMIT" and args.price is None:
            print(Fore.RED + "Error: --price is required for LIMIT orders.")
            sys.exit(1)
            
        run_args_mode(args)
