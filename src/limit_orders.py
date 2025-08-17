import os
from binance.client import Client
from dotenv import load_dotenv

# Load API keys
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET, testnet=True)

def place_limit_order(symbol, side, quantity, price):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce="GTC",  # Good Till Cancelled
            quantity=quantity,
            price=price
        )
        print("✅ Limit order placed successfully:", order)
    except Exception as e:
        print("❌ Error placing limit order:", e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: python src/limit_orders.py <symbol> <BUY/SELL> <quantity> <price>")
        exit(1)

    symbol = sys.argv[1]
    side = sys.argv[2].upper()
    quantity = float(sys.argv[3])
    price = float(sys.argv[4])

    place_limit_order(symbol, side, quantity, price)
