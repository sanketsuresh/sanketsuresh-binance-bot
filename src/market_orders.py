import os
from binance.client import Client
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# If not found, ask user and save to .env
if not API_KEY or not API_SECRET:
    API_KEY = input("Enter your Binance API Key: ")
    API_SECRET = input("Enter your Binance API Secret: ")
    with open(".env", "w") as f:
        f.write(f"API_KEY={API_KEY}\nAPI_SECRET={API_SECRET}\n")

# Connect to Binance Testnet
client = Client(API_KEY, API_SECRET, testnet=True)

def place_market_order(symbol, side, quantity):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        print("✅ Order placed successfully:", order)
    except Exception as e:
        print("❌ Error placing order:", e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python src/market_orders.py <symbol> <BUY/SELL> <quantity>")
        exit(1)

    symbol = sys.argv[1]
    side = sys.argv[2].upper()
    quantity = float(sys.argv[3])

    place_market_order(symbol, side, quantity)
