# Sanket's Binance Futures Trading Bot

A comprehensive Python-based trading bot for Binance Futures Testnet with support for market orders, limit orders, stop-limit orders, and OCO (One-Cancels-Other) orders.

## 🚀 Features

### Core Features ✅
- **Market Orders**: Execute immediate buy/sell orders at current market price
- **Limit Orders**: Place orders at specific price levels with good-till-cancelled (GTC) functionality
- **Advanced Stop-Limit Orders**: Set stop-loss and take-profit strategies with trigger mechanisms
- **OCO Orders**: Simulate One-Cancels-Other functionality using dual order placement

### Technical Features 🛠️
- **Binance Testnet Integration**: Safe testing environment using testnet.binancefuture.com
- **Automatic API Key Management**: Secure storage and auto-loading from `.env` file
- **Comprehensive Input Validation**: Symbol format, quantity, and price validation
- **Detailed Logging**: All API calls, responses, and errors logged to `bot.log`
- **CLI Interface**: Easy-to-use command-line interface for all operations
- **Error Handling**: Robust exception handling for API errors and network issues

## 📁 Project Structure

```
sanket_binance_bot/
│
├── src/
│   ├── market_orders.py       # Market order execution
│   ├── limit_orders.py        # Limit order placement
│   ├── advanced/              # Advanced trading features
│   │   ├── stop_limit.py      # Stop-limit orders
│   │   └── oco.py             # OCO order simulation
│
├── bot.log                    # Auto-generated log file
├── .env                       # API credentials (auto-created)
├── README.md                  # This documentation
├── requirements.txt           # Python dependencies
└── report.pdf                 # Project explanation & screenshots
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+ installed
- Binance Futures Testnet account
- API Key and Secret from Binance Testnet

### Step 1: Clone and Setup
```bash
# Navigate to the project directory
cd sanket_binance_bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: API Key Configuration

**First Run**: When you run any module for the first time, you'll be prompted to enter your API credentials:

```
API credentials not found in .env file. Please enter them:
Enter your Binance API Key: your_api_key_here
Enter your Binance API Secret: your_api_secret_here
```

The bot will automatically create a `.env` file:
```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

**Subsequent Runs**: The bot automatically loads credentials from the `.env` file.

### Step 4: Get Binance Testnet API Keys

1. Visit [Binance Testnet](https://testnet.binancefuture.com/)
2. Create an account or log in
3. Generate API Key and Secret
4. Enable Futures Trading permissions

## 🎯 Usage Examples

### Market Orders
Execute immediate buy/sell orders at current market price.

```bash
# Buy 0.01 BTC at current market price
python src/market_orders.py BTCUSDT BUY 0.01

# Sell 0.005 ETH at current market price
python src/market_orders.py ETHUSDT SELL 0.005
```

**Market Order Logic**:
- Executes immediately at best available market price
- No price specification required
- Suitable for urgent trades

### Limit Orders
Place orders at specific price levels.

```bash
# Sell 0.01 BTC when price reaches $29,000
python src/limit_orders.py BTCUSDT SELL 0.01 29000

# Buy 0.1 ETH when price drops to $1,800
python src/limit_orders.py ETHUSDT BUY 0.1 1800
```

**Limit Order Logic**:
- Order waits in the order book until price is reached
- Good-Till-Cancelled (GTC) by default
- Shows price comparison with current market price

### Advanced Stop-Limit Orders
Set trigger-based orders for risk management.

```bash
# Stop-loss: Sell 0.01 BTC if price drops to $28,500, execute at $28,000
python src/advanced/stop_limit.py BTCUSDT SELL 0.01 28500 28000

# Stop-buy: Buy 0.01 BTC if price rises to $30,500, execute at $31,000
python src/advanced/stop_limit.py BTCUSDT BUY 0.01 30500 31000
```

**Stop-Limit Order Logic**:
- **SELL**: When price drops to stop price, place limit sell order
- **BUY**: When price rises to stop price, place limit buy order
- Combines stop-loss protection with price control

### OCO Orders (Advanced)
Simulate One-Cancels-Other functionality.

```bash
# OCO: Take profit at $30,000 OR stop-loss at $28,000
python src/advanced/oco.py BTCUSDT SELL 0.01 30000 28500 28000
```

**OCO Parameters**:
1. `SYMBOL`: Trading pair (e.g., BTCUSDT)
2. `SIDE`: BUY or SELL
3. `QUANTITY`: Amount to trade
4. `LIMIT_PRICE`: Profit-taking price
5. `STOP_PRICE`: Trigger price for stop-loss
6. `STOP_LIMIT_PRICE`: Execution price for stop-loss

⚠️ **Important**: Binance Futures doesn't support native OCO. This creates two separate orders that require manual management.

## 📊 Logging & Monitoring

All bot activities are logged to `bot.log` with timestamps:

```log
2024-01-20 15:30:15,123 - INFO - Starting market order execution: BUY 0.01 BTCUSDT
2024-01-20 15:30:15,456 - INFO - Connected to Binance Testnet
2024-01-20 15:30:16,789 - INFO - Current market price for BTCUSDT: $29156.50
2024-01-20 15:30:17,234 - INFO - Order placed successfully!
2024-01-20 15:30:17,235 - INFO - Order ID: 123456789
```

**Log Features**:
- All API calls and responses
- Order execution details
- Error messages and warnings
- Account balance information
- Price comparisons

## ⚙️ Configuration Options

### Environment Variables (.env)
```env
API_KEY=your_binance_testnet_api_key
API_SECRET=your_binance_testnet_secret_key
```

### Testnet Configuration
The bot is pre-configured for Binance Futures Testnet:
- Base URL: `https://testnet.binancefuture.com`
- Safe testing environment
- No real money involved

To switch to mainnet (⚠️ **USE WITH CAUTION**):
```python
# In each module, change:
client = create_binance_client(api_key, api_secret, testnet=False)
```

## 🛡️ Input Validation

The bot includes comprehensive validation:

### Symbol Validation
- Must be at least 6 characters (e.g., BTCUSDT)
- Automatically converted to uppercase

### Side Validation
- Must be either "BUY" or "SELL" (case-insensitive)

### Quantity Validation
- Must be a positive number greater than 0
- Supports decimal quantities (e.g., 0.01, 0.001)

### Price Validation
- Must be a positive number greater than 0
- Automatic price logic validation for advanced orders

### Advanced Order Logic Validation
- **Stop-Limit**: Validates stop/limit price relationships
- **OCO**: Ensures proper profit/loss price configuration

## 🚨 Error Handling

### Common Error Types
1. **API Errors**: Invalid credentials, rate limits, server issues
2. **Order Errors**: Insufficient balance, invalid parameters
3. **Network Errors**: Connection timeouts, DNS issues
4. **Validation Errors**: Invalid input parameters

### Error Recovery
- Automatic retry for transient network issues
- Detailed error logging for debugging
- Safe cancellation of partial OCO orders
- Clear error messages for user action

## 📈 Trading Strategies

### Market Making
Use limit orders to provide liquidity:
```bash
# Place buy order below market
python src/limit_orders.py BTCUSDT BUY 0.01 28000

# Place sell order above market  
python src/limit_orders.py BTCUSDT SELL 0.01 30000
```

### Risk Management
Use stop-limit orders for protection:
```bash
# Protect long position with stop-loss
python src/advanced/stop_limit.py BTCUSDT SELL 0.01 28500 28000
```

### Bracket Trading
Use OCO for comprehensive position management:
```bash
# Complete position management: profit OR stop-loss
python src/advanced/oco.py BTCUSDT SELL 0.01 31000 28500 28000
```

## 🔍 Troubleshooting

### Common Issues

**Issue**: `API credentials are required`
- **Solution**: Ensure `.env` file exists with valid API keys
- **Check**: Verify API keys have Futures trading permissions

**Issue**: `Binance API Error: Invalid symbol`
- **Solution**: Use correct symbol format (e.g., BTCUSDT, not BTC-USDT)
- **Check**: Verify symbol exists on Binance Futures

**Issue**: `Order Error: Insufficient balance`
- **Solution**: Add testnet funds to your account
- **Check**: Verify account balance with test USDT

**Issue**: `Network connection error`
- **Solution**: Check internet connection
- **Check**: Verify testnet.binancefuture.com is accessible

### Debug Mode
Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📋 Dependencies

Core dependencies from `requirements.txt`:
- `python-binance==1.0.29` - Binance API wrapper
- `python-dotenv==1.1.1` - Environment variable management  
- `requests>=2.32.0` - HTTP requests
- `websockets>=15.0.0` - WebSocket support
- `aiohttp>=3.12.0` - Async HTTP client
- `pycryptodome>=3.23.0` - Cryptographic functions

## 🔒 Security Considerations

### API Key Security
- Store API keys in `.env` file (not in code)
- Add `.env` to `.gitignore` 
- Use testnet keys for development
- Never share API secrets

### Testnet Safety
- Always test on Binance Testnet first
- Verify all functionality before mainnet use
- Use small quantities for testing

### Risk Management
- Set appropriate stop-losses
- Never risk more than you can afford to lose
- Monitor positions actively
- Use position sizing strategies

## 🤝 Contributing

To extend the bot functionality:

1. Follow existing code structure
2. Add comprehensive logging
3. Include input validation
4. Write clear documentation
5. Test on testnet thoroughly

## 📜 License

This project is for educational purposes. Use at your own risk. The author is not responsible for any financial losses.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log file (`bot.log`)
3. Verify API credentials and permissions
4. Test with smaller quantities first

---

**⚠️ DISCLAIMER**: This bot is designed for educational purposes and testnet use. Always test thoroughly on testnet before considering any mainnet usage. Trading cryptocurrencies involves substantial risk of loss.
