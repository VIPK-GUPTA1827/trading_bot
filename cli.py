import sys
import argparse
from client import BinanceTestnetClient, log_message

def main():
    # Setup command-line argument parser
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot CLI")
    
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="BUY or SELL side")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT"], help="MARKET or LIMIT order type")
    parser.add_argument("--quantity", type=float, help="Order quantity (number of coins)")
    parser.add_argument("--price", type=float, help="Order price (required only for LIMIT orders)")
    parser.add_argument("--mock", action="store_true", help="Force Simulation (Mock) Mode")
    parser.add_argument("--test-connection", action="store_true", help="Test connection to server only")

    args = parser.parse_args()
    client = BinanceTestnetClient()

    # 1. Connection check flow
    if args.test_connection:
        log_message("Testing connection to Binance Futures Testnet...")
        try:
            server_time = client.get_server_time()
            log_message(f"Connection Successful! Server Time: {server_time}")
        except Exception as e:
            log_message(f"Connection Failed: {e}")
        return

    # 2. Argument validation flow
    # Symbol, side, type, quantity are required for placing orders
    if not args.symbol or not args.side or not args.type or not args.quantity:
        print("\n==================================================")
        print("         Binance Futures Trading Bot CLI          ")
        print("==================================================")
        print("Usage Examples:")
        print("  Test Connection:  python cli.py --test-connection")
        print("  Place Market Order: python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002")
        print("  Place Limit Order:  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 98000")
        print("  Force Mock Mode:   python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --mock")
        print("==================================================")
        print("Run with --help to see details of all flags.")
        return

    # Price validation check for limit order
    if args.type.upper() == "LIMIT" and args.price is None:
        print("Error: --price is required for LIMIT orders.")
        sys.exit(1)

    # 3. Order placement flow
    try:
        result = client.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            mock=args.mock
        )
        
        # Display order execution details
        print("\n--------------------------------------------------")
        print("                 ORDER SUCCESSFUL                 ")
        print("--------------------------------------------------")
        print(f"Order ID:      {result.get('orderId')}")
        print(f"Symbol:        {result.get('symbol')}")
        print(f"Status:        {result.get('status')}")
        print(f"Side:          {result.get('side')}")
        print(f"Type:          {result.get('type')}")
        print(f"Quantity:      {result.get('origQty')}")
        print(f"Price:         {result.get('price')}")
        print("--------------------------------------------------\n")

    except Exception as e:
        print("\n--------------------------------------------------")
        print("                  ORDER FAILED                    ")
        print("--------------------------------------------------")
        print(f"Error details: {e}")
        print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()
