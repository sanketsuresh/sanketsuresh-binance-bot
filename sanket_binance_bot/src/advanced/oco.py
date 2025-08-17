#!/usr/bin/env python3
"""
Binance Futures OCO (One-Cancels-Other) Orders Module (Advanced)
Handles OCO orders with CLI interface
Usage: python src/advanced/oco.py SYMBOL SIDE QUANTITY LIMIT_PRICE STOP_PRICE STOP_LIMIT_PRICE
Example: python src/advanced/oco.py BTCUSDT SELL 0.01 30000 28500 28000

OCO Order Logic:
- Places two orders simultaneously: a limit order and a stop-limit order
- When one order is filled, the other is automatically cancelled
- Useful for profit-taking and stop-loss management
"""

import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

# Add parent directory to path to import common functions
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def setup_logging():
    """Setup logging configuration"""
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bot.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),  # Append mode
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_api_credentials():
    """Get API credentials from .env file or prompt user"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_file)
    
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    
    if not api_key or not api_secret:
        logger.info("API credentials not found in .env file. Please enter them:")
        api_key = input("Enter your Binance API Key: ").strip()
        api_secret = input("Enter your Binance API Secret: ").strip()
        
        # Save to .env file
        try:
            with open(env_file, 'w') as f:
                f.write(f"API_KEY={api_key}\n")
                f.write(f"API_SECRET={api_secret}\n")
            logger.info(f"API credentials saved to {env_file}")
        except Exception as e:
            logger.error(f"Error saving credentials to .env file: {e}")
    
    return api_key, api_secret


def validate_inputs(symbol, side, quantity, limit_price, stop_price, stop_limit_price):
    """Validate input parameters"""
    errors = []
    
    # Validate symbol format
    if not symbol or len(symbol) < 6:
        errors.append("Symbol must be at least 6 characters (e.g., BTCUSDT)")
    
    # Validate side
    if side.upper() not in ['BUY', 'SELL']:
        errors.append("Side must be either BUY or SELL")
    
    # Validate quantity
    try:
        qty = float(quantity)
        if qty <= 0:
            errors.append("Quantity must be greater than 0")
    except ValueError:
        errors.append("Quantity must be a valid number")
    
    # Validate limit price
    try:
        limit_prc = float(limit_price)
        if limit_prc <= 0:
            errors.append("Limit price must be greater than 0")
    except ValueError:
        errors.append("Limit price must be a valid number")
    
    # Validate stop price
    try:
        stop_prc = float(stop_price)
        if stop_prc <= 0:
            errors.append("Stop price must be greater than 0")
    except ValueError:
        errors.append("Stop price must be a valid number")
    
    # Validate stop limit price
    try:
        stop_limit_prc = float(stop_limit_price)
        if stop_limit_prc <= 0:
            errors.append("Stop limit price must be greater than 0")
    except ValueError:
        errors.append("Stop limit price must be a valid number")
    
    # Validate OCO logic
    try:
        limit_prc = float(limit_price)
        stop_prc = float(stop_price)
        stop_limit_prc = float(stop_limit_price)
        
        if side.upper() == 'SELL':
            # For sell orders: limit price should be above stop price (profit above, loss below)
            if limit_prc <= stop_prc:
                errors.append("For SELL OCO: limit price should be > stop price (profit taking above current, stop loss below)")
            # Stop limit price should be <= stop price
            if stop_limit_prc > stop_prc:
                errors.append("For SELL OCO: stop limit price should be <= stop price")
        else:  # BUY
            # For buy orders: limit price should be below stop price (buy low, stop loss above)
            if limit_prc >= stop_prc:
                errors.append("For BUY OCO: limit price should be < stop price (buy below current, stop loss above)")
            # Stop limit price should be >= stop price
            if stop_limit_prc < stop_prc:
                errors.append("For BUY OCO: stop limit price should be >= stop price")
    except ValueError:
        pass  # Already handled above
    
    return errors


def create_binance_client(api_key, api_secret, testnet=True):
    """Create Binance client with testnet configuration"""
    try:
        client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            # Set testnet base URL for futures
            client.API_URL = 'https://testnet.binancefuture.com'
            client.FUTURES_URL = 'https://testnet.binancefuture.com'
        
        logger.info(f"Connected to Binance {'Testnet' if testnet else 'Mainnet'}")
        return client
    except Exception as e:
        logger.error(f"Error creating Binance client: {e}")
        raise


def get_current_price(client, symbol):
    """Get current market price for the symbol"""
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol.upper())
        current_price = float(ticker['price'])
        logger.info(f"Current market price for {symbol}: ${current_price}")
        return current_price
    except Exception as e:
        logger.error(f"Error getting current price: {e}")
        return None


def place_oco_order(client, symbol, side, quantity, limit_price, stop_price, stop_limit_price):
    """
    Place an OCO (One-Cancels-Other) order on Binance Futures
    Note: Binance Futures doesn't have native OCO support, so we simulate it with two separate orders
    """
    try:
        logger.info(f"Placing OCO {side} order:")
        logger.info(f"  Symbol: {symbol}")
        logger.info(f"  Quantity: {quantity}")
        logger.info(f"  Limit Price: ${limit_price} (profit taking)")
        logger.info(f"  Stop Price: ${stop_price} (trigger)")
        logger.info(f"  Stop Limit Price: ${stop_limit_price} (stop loss execution)")
        
        # Get current price for reference
        current_price = get_current_price(client, symbol)
        if current_price:
            limit_diff = float(limit_price) - current_price
            stop_diff = float(stop_price) - current_price
            stop_limit_diff = float(stop_limit_price) - current_price
            logger.info(f"Limit price vs current: ${limit_diff:+.2f}")
            logger.info(f"Stop price vs current: ${stop_diff:+.2f}")
            logger.info(f"Stop limit price vs current: ${stop_limit_diff:+.2f}")
        
        # Since Binance Futures doesn't have native OCO, we place two separate orders
        # and rely on manual management or additional logic to cancel the other when one fills
        
        logger.info("⚠️  Note: Binance Futures doesn't support native OCO orders.")
        logger.info("   This will place two separate orders that need manual management.")
        logger.info("   Consider using a more sophisticated bot for automatic OCO management.")
        
        orders = []
        
        # Place the limit order (profit taking)
        logger.info("Placing limit order (profit taking)...")
        limit_order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=limit_price
        )
        orders.append(limit_order)
        logger.info(f"Limit order placed - Order ID: {limit_order['orderId']}")
        
        # Place the stop-limit order (stop loss)
        logger.info("Placing stop-limit order (stop loss)...")
        stop_order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type='STOP',
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=stop_limit_price,
            stopPrice=stop_price
        )
        orders.append(stop_order)
        logger.info(f"Stop-limit order placed - Order ID: {stop_order['orderId']}")
        
        logger.info(f"OCO simulation completed!")
        logger.info(f"Limit Order ID: {limit_order['orderId']} @ ${limit_order['price']}")
        logger.info(f"Stop Order ID: {stop_order['orderId']} @ ${stop_order['price']} (Stop: ${stop_order['stopPrice']})")
        logger.info("⚠️  Remember to manually cancel the other order when one fills!")
        
        return orders
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e}")
        # If we managed to place one order but not the other, we should try to cancel the first
        if orders:
            logger.info("Attempting to cancel partially placed orders...")
            for order in orders:
                try:
                    client.futures_cancel_order(symbol=symbol.upper(), orderId=order['orderId'])
                    logger.info(f"Cancelled order {order['orderId']}")
                except:
                    logger.error(f"Failed to cancel order {order['orderId']}")
        raise
    except BinanceOrderException as e:
        logger.error(f"Binance Order Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing OCO orders: {e}")
        raise


def get_open_orders(client, symbol=None):
    """Get open orders for the account"""
    try:
        if symbol:
            orders = client.futures_get_open_orders(symbol=symbol.upper())
        else:
            orders = client.futures_get_open_orders()
        
        if orders:
            logger.info(f"Found {len(orders)} open order(s):")
            for order in orders:
                if order.get('stopPrice'):
                    logger.info(f"  Order ID: {order['orderId']} | {order['type']} {order['side']} {order['origQty']} {order['symbol']} @ ${order['price']} (Stop: ${order['stopPrice']})")
                else:
                    logger.info(f"  Order ID: {order['orderId']} | {order['type']} {order['side']} {order['origQty']} {order['symbol']} @ ${order['price']}")
        else:
            logger.info("No open orders found")
        
        return orders
    except Exception as e:
        logger.error(f"Error getting open orders: {e}")
        return []


def explain_oco_order(side, limit_price, stop_price, stop_limit_price, current_price):
    """Explain the OCO order logic to the user"""
    logger.info("=== OCO ORDER EXPLANATION ===")
    
    if side.upper() == 'SELL':
        logger.info(f"SELL OCO Order (Profit Taking + Stop Loss):")
        logger.info(f"• Current Price: ${current_price}")
        logger.info(f"• Limit Order: ${limit_price} (profit taking - sell if price goes UP)")
        logger.info(f"• Stop Price: ${stop_price} (trigger for stop loss)")
        logger.info(f"• Stop Limit: ${stop_limit_price} (stop loss execution - sell if price goes DOWN)")
        logger.info(f"• Logic: Either take profit at ${limit_price} OR stop loss at ${stop_limit_price}")
    else:  # BUY
        logger.info(f"BUY OCO Order (Buy Low + Stop Loss):")
        logger.info(f"• Current Price: ${current_price}")
        logger.info(f"• Limit Order: ${limit_price} (buy if price goes DOWN)")
        logger.info(f"• Stop Price: ${stop_price} (trigger for stop loss)")
        logger.info(f"• Stop Limit: ${stop_limit_price} (stop loss execution - buy if price goes UP)")
        logger.info(f"• Logic: Either buy low at ${limit_price} OR stop loss at ${stop_limit_price}")
    
    logger.info("⚠️  IMPORTANT: This is a simulated OCO using two separate orders!")
    logger.info("   You must manually cancel the remaining order when one fills.")
    logger.info("==============================")


def get_account_info(client):
    """Get account information for verification"""
    try:
        account = client.futures_account()
        balance = client.futures_account_balance()
        
        logger.info("Account Information:")
        logger.info(f"Total Wallet Balance: {account.get('totalWalletBalance', 'N/A')} USDT")
        logger.info(f"Available Balance: {account.get('availableBalance', 'N/A')} USDT")
        
        return account, balance
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return None, None


def main():
    """Main function to handle CLI interface"""
    global logger
    logger = setup_logging()
    
    # Check command line arguments
    if len(sys.argv) != 7:
        print("Usage: python src/advanced/oco.py SYMBOL SIDE QUANTITY LIMIT_PRICE STOP_PRICE STOP_LIMIT_PRICE")
        print("Example: python src/advanced/oco.py BTCUSDT SELL 0.01 30000 28500 28000")
        print("")
        print("OCO Order Logic:")
        print("• SELL: Take profit at LIMIT_PRICE (above current) OR stop loss at STOP_LIMIT_PRICE (below current)")
        print("• BUY: Buy at LIMIT_PRICE (below current) OR stop loss at STOP_LIMIT_PRICE (above current)")
        print("")
        print("⚠️  Note: This simulates OCO using two separate orders (manual management required)")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    limit_price = sys.argv[4]
    stop_price = sys.argv[5]
    stop_limit_price = sys.argv[6]
    
    logger.info(f"Starting OCO order execution:")
    logger.info(f"  {side} {quantity} {symbol}")
    logger.info(f"  Limit Price: ${limit_price}")
    logger.info(f"  Stop Price: ${stop_price}")
    logger.info(f"  Stop Limit Price: ${stop_limit_price}")
    
    # Validate inputs
    validation_errors = validate_inputs(symbol, side, quantity, limit_price, stop_price, stop_limit_price)
    if validation_errors:
        logger.error("Input validation failed:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    try:
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        if not api_key or not api_secret:
            logger.error("API credentials are required")
            sys.exit(1)
        
        # Create Binance client (using testnet)
        client = create_binance_client(api_key, api_secret, testnet=True)
        
        # Get account info and current price
        get_account_info(client)
        current_price = get_current_price(client, symbol)
        
        # Explain the order logic
        explain_oco_order(side, limit_price, stop_price, stop_limit_price, current_price)
        
        # Show existing open orders
        get_open_orders(client, symbol)
        
        # Confirm before placing orders
        print("\n⚠️  This will place TWO separate orders to simulate OCO functionality.")
        print("   You will need to manually manage them (cancel one when the other fills).")
        confirm = input("Do you want to proceed? (y/N): ").strip().lower()
        
        if confirm != 'y':
            logger.info("Operation cancelled by user")
            sys.exit(0)
        
        # Place the OCO orders
        orders = place_oco_order(client, symbol, side, quantity, limit_price, stop_price, stop_limit_price)
        
        logger.info("OCO orders placed successfully!")
        print(f"Limit Order ID: {orders[0]['orderId']} @ ${orders[0]['price']}")
        print(f"Stop Order ID: {orders[1]['orderId']} @ ${orders[1]['price']} (Stop: ${orders[1]['stopPrice']})")
        print("⚠️  Remember to cancel the other order when one fills!")
        
        # Show updated open orders
        logger.info("Updated open orders:")
        get_open_orders(client, symbol)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"OCO order failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
