#!/usr/bin/env python3
"""
Binance Futures Stop-Limit Orders Module (Advanced)
Handles stop-limit orders with CLI interface
Usage: python src/advanced/stop_limit.py SYMBOL SIDE QUANTITY STOP_PRICE LIMIT_PRICE
Example: python src/advanced/stop_limit.py BTCUSDT SELL 0.01 28500 28000
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


def validate_inputs(symbol, side, quantity, stop_price, limit_price):
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
    
    # Validate stop price
    try:
        stop_prc = float(stop_price)
        if stop_prc <= 0:
            errors.append("Stop price must be greater than 0")
    except ValueError:
        errors.append("Stop price must be a valid number")
    
    # Validate limit price
    try:
        limit_prc = float(limit_price)
        if limit_prc <= 0:
            errors.append("Limit price must be greater than 0")
    except ValueError:
        errors.append("Limit price must be a valid number")
    
    # Validate stop-limit logic
    try:
        stop_prc = float(stop_price)
        limit_prc = float(limit_price)
        
        if side.upper() == 'SELL':
            # For sell orders, stop price should be higher than limit price
            # (stop-loss scenario: sell when price drops to stop_price at limit_price)
            if stop_prc < limit_prc:
                errors.append("For SELL orders: stop price should be >= limit price (stop-loss scenario)")
        else:  # BUY
            # For buy orders, stop price should be higher than limit price  
            # (stop-buy scenario: buy when price rises to stop_price at limit_price)
            if stop_prc < limit_prc:
                errors.append("For BUY orders: stop price should be >= limit price (stop-buy scenario)")
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


def place_stop_limit_order(client, symbol, side, quantity, stop_price, limit_price):
    """Place a stop-limit order on Binance Futures"""
    try:
        logger.info(f"Placing stop-limit {side} order:")
        logger.info(f"  Symbol: {symbol}")
        logger.info(f"  Quantity: {quantity}")
        logger.info(f"  Stop Price: ${stop_price}")
        logger.info(f"  Limit Price: ${limit_price}")
        
        # Get current price for reference
        current_price = get_current_price(client, symbol)
        if current_price:
            stop_diff = float(stop_price) - current_price
            limit_diff = float(limit_price) - current_price
            logger.info(f"Stop price vs current: ${stop_diff:+.2f}")
            logger.info(f"Limit price vs current: ${limit_diff:+.2f}")
        
        # Place the stop-limit order
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type='STOP',  # Stop-limit order type
            timeInForce=Client.TIME_IN_FORCE_GTC,  # Good Till Cancelled
            quantity=quantity,
            price=limit_price,  # The limit price
            stopPrice=stop_price  # The stop price (trigger price)
        )
        
        logger.info(f"Stop-limit order placed successfully!")
        logger.info(f"Order ID: {order['orderId']}")
        logger.info(f"Symbol: {order['symbol']}")
        logger.info(f"Side: {order['side']}")
        logger.info(f"Type: {order['type']}")
        logger.info(f"Quantity: {order['origQty']}")
        logger.info(f"Stop Price: ${order['stopPrice']}")
        logger.info(f"Limit Price: ${order['price']}")
        logger.info(f"Status: {order['status']}")
        logger.info(f"Time in Force: {order['timeInForce']}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e}")
        raise
    except BinanceOrderException as e:
        logger.error(f"Binance Order Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing order: {e}")
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


def explain_stop_limit_order(side, stop_price, limit_price, current_price):
    """Explain the stop-limit order logic to the user"""
    logger.info("=== STOP-LIMIT ORDER EXPLANATION ===")
    
    if side.upper() == 'SELL':
        logger.info(f"SELL Stop-Limit Order (Stop-Loss):")
        logger.info(f"• Current Price: ${current_price}")
        logger.info(f"• Stop Price: ${stop_price} (trigger)")
        logger.info(f"• Limit Price: ${limit_price} (execution)")
        logger.info(f"• Logic: When price drops to ${stop_price}, place a limit sell order at ${limit_price}")
        if current_price and float(stop_price) > current_price:
            logger.warning("⚠️  Stop price is above current market price - this may trigger immediately!")
    else:  # BUY
        logger.info(f"BUY Stop-Limit Order (Stop-Buy):")
        logger.info(f"• Current Price: ${current_price}")
        logger.info(f"• Stop Price: ${stop_price} (trigger)")
        logger.info(f"• Limit Price: ${limit_price} (execution)")
        logger.info(f"• Logic: When price rises to ${stop_price}, place a limit buy order at ${limit_price}")
        if current_price and float(stop_price) < current_price:
            logger.warning("⚠️  Stop price is below current market price - this may trigger immediately!")
    
    logger.info("=====================================")


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
    if len(sys.argv) != 6:
        print("Usage: python src/advanced/stop_limit.py SYMBOL SIDE QUANTITY STOP_PRICE LIMIT_PRICE")
        print("Example: python src/advanced/stop_limit.py BTCUSDT SELL 0.01 28500 28000")
        print("")
        print("Stop-Limit Order Logic:")
        print("• SELL: Triggers when price drops to STOP_PRICE, then places limit order at LIMIT_PRICE")
        print("• BUY: Triggers when price rises to STOP_PRICE, then places limit order at LIMIT_PRICE")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    stop_price = sys.argv[4]
    limit_price = sys.argv[5]
    
    logger.info(f"Starting stop-limit order execution:")
    logger.info(f"  {side} {quantity} {symbol}")
    logger.info(f"  Stop Price: ${stop_price}")
    logger.info(f"  Limit Price: ${limit_price}")
    
    # Validate inputs
    validation_errors = validate_inputs(symbol, side, quantity, stop_price, limit_price)
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
        explain_stop_limit_order(side, stop_price, limit_price, current_price)
        
        # Show existing open orders
        get_open_orders(client, symbol)
        
        # Place the stop-limit order
        order = place_stop_limit_order(client, symbol, side, quantity, stop_price, limit_price)
        
        logger.info("Stop-limit order placed successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Status: {order['status']}")
        print(f"Stop Price: ${order['stopPrice']}")
        print(f"Limit Price: ${order['price']}")
        
        # Show updated open orders
        logger.info("Updated open orders:")
        get_open_orders(client, symbol)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Stop-limit order failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
