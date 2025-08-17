📄 .gitignore
# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
*.sqlite3

# Virtual environments
venv/
env/
.venv/

# Secrets
.env
*.key
*.pem

# OS files
.DS_Store
Thumbs.db

📄 requirements.txt
python-binance
requests
python-dotenv

📄 README.md
# Binance Futures Trading Bot

A CLI-based Binance Futures Trading Bot built in Python.  
This bot works on the **Binance USDT-M Futures Testnet** and supports market and limit orders with proper validation, logging, and error handling.  
Bonus advanced order types (OCO, Stop-Limit, TWAP, Grid) are also included.

---

## 🚀 Features
- ✅ Market Orders (Buy/Sell)
- ✅ Limit Orders (Buy/Sell)
- 🔒 Input validation (symbol, quantity, price)
- 📝 Structured Logging (`bot.log`)
- 🛑 Error handling with messages
- ✨ Optional Advanced Orders:
  - Stop-Limit Orders
  - OCO (One-Cancels-the-Other)
  - TWAP (Time Weighted Average Price)
  - Grid Orders

---

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/sanketsuresh/sanketsuresh-binance-bot.git
   cd sanketsuresh-bot


Create a virtual environment (recommended):

python3 -m venv venv
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

🔑 Setup

Register and activate a Binance Testnet Account

Generate API Key & Secret

Create a .env file in the project root:

API_KEY=your_api_key
API_SECRET=your_api_secret

▶️ Usage
Place a Market Order
python src/market_orders.py BTCUSDT BUY 0.01

Place a Limit Order
python src/limit_orders.py BTCUSDT SELL 0.01 45000


Logs will be stored in bot.log.

📊 Report

See report.pdf for implementation details, screenshots, and explanation.

👤 Author

Sanket Suresh Basaragaon
📧 sanketsuresh000@gmail.com | 📱 7411178329


---

## 📄 Git Commands (final push)
Copy–paste these in terminal (inside project folder):  

```bash
# Remove venv if accidentally added
rm -rf venv
echo "venv/" >> .gitignore
git rm -r --cached venv

# Add files
git add .
git commit -m "Final clean commit with README, requirements, .gitignore"

# Push to GitHub
git push -u origin main --force
