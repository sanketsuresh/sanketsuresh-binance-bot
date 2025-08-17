#!/usr/bin/env python3
"""
Binance Futures Market Orders Module
Handles market buy and sell orders with CLI interface
Usage: python src/market_orders.py SYMBOL SIDE QUANTITY
Example: python src/market_orders.py BTCUSDT BUY 0.01
"""

import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException


def setup_logging():
    """Setup logging configuration"""
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_api_credentials():
    """Get API credentials from .env file or prompt user"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
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


def validate_inputs(symbol, side, quantity):
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


def place_market_order(client, symbol, side, quantity):
    """Place a market order on Binance Futures"""
    try:
        logger.info(f"Placing market {side} order: {quantity} {symbol}")
        
        # Place the market order
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )
        
        logger.info(f"Order placed successfully!")
        logger.info(f"Order ID: {order['orderId']}")
        logger.info(f"Symbol: {order['symbol']}")
        logger.info(f"Side: {order['side']}")
        logger.info(f"Quantity: {order['origQty']}")
        logger.info(f"Status: {order['status']}")
        
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
    if len(sys.argv) != 4:
        print("Usage: python src/market_orders.py SYMBOL SIDE QUANTITY")
        print("Example: python src/market_orders.py BTCUSDT BUY 0.01")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    
    logger.info(f"Starting market order execution: {side} {quantity} {symbol}")
    
    # Validate inputs
    validation_errors = validate_inputs(symbol, side, quantity)
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
        
        # Get account info
        get_account_info(client)
        
        # Place the market order
        order = place_market_order(client, symbol, side, quantity)
        
        logger.info("Market order completed successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Status: {order['status']}")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Market order failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
