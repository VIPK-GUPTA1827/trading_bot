import sys
from client import BinanceTestnetClient

def main():
    print("--------------------------------------------------")
    print("Testing connection to Binance Futures Testnet...")
    print("--------------------------------------------------")
    
    # client object create karenge
    client = BinanceTestnetClient()
    
    try:
        # get_server_time call karke check karenge connection
        server_time = client.get_server_time()
        print("Status: Success!")
        print(f"Binance Server Time (Epoch Milliseconds): {server_time}")
        print("--------------------------------------------------")
    except Exception as e:
        print("Status: Failed!")
        print(f"Error detail: {e}")
        print("--------------------------------------------------")

if __name__ == "__main__":
    main()
