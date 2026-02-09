from flask import Flask, render_template, request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Stability configuration
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

SYMBOLS = {'USD': '$', 'KES': 'KSh', 'EUR': '€', 'GBP': '£'}
CRYPTO_ASSETS = {'bitcoin': 'Bitcoin', 'ethereum': 'Ethereum', 'dogecoin': 'Dogecoin'}
OTHER_ASSETS = {'gold': 'Gold', 'oil': 'Oil'}
STOCK_ASSETS = {'AAPL': 'Apple Inc.', 'NVDA': 'NVIDIA', 'TSLA': 'Tesla'}

def get_market_price(asset_id, currency):
    # This function is only for crypto via CoinGecko
    if asset_id not in CRYPTO_ASSETS:
        return None
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies={currency.lower()}"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data.get(asset_id, {}).get(currency.lower()))
    except requests.exceptions.RequestException:
        return None

def get_crypto_market_chart(asset_id, currency, days='30'):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency={currency.lower()}&days={days}"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('prices')
    except requests.exceptions.RequestException:
        return None

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/chart-data/crypto/<asset_id>')
def crypto_chart_data(asset_id):
    prices = get_crypto_market_chart(asset_id, currency='usd', days='30')
    if prices:
        return {'prices': prices}
    return {'error': 'Could not fetch data'}, 404

@app.route('/chart-data/stock/<symbol>')
def stock_chart_data(symbol):
    # --- IMPORTANT ---
    # This is using dummy data because a real-time stock API (like Alpha Vantage or Finnhub)
    # typically requires an API key. You would replace this with a real API call.
    # Generating some random-walk dummy data for demonstration.
    prices = []
    price = random.uniform(150, 200) # Start price for a stock like AAPL
    now_dt = datetime.now()
    for i in range(30):
        timestamp = (now_dt - timedelta(days=29-i)).timestamp() * 1000
        price *= random.uniform(0.98, 1.02)
        prices.append([timestamp, price])
    return {'prices': prices}

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    asset_type = request.args.get('type', 'other')
    
    # Default assets if none are selected
    default_asset = 'gold' if asset_type == 'other' else 'AAPL'
    
    # Checks URL first (for dropdowns), then the form (for Sync button)
    selected_asset = request.args.get('asset') or request.form.get('asset_id', default_asset)
    assets = OTHER_ASSETS if asset_type == 'other' else STOCK_ASSETS
    
    # --- This section has hardcoded portfolio values for demonstration ---
    # In a real app, this would come from a database for the logged-in user.
    if selected_asset == 'bitcoin':
        qty = float(request.form.get('qty', 0.00009644)) # Your BTC holding
        buy_price_ksh = 1200.0 # Your initial investment
    elif selected_asset == 'ethereum':
        qty = float(request.form.get('qty', 0.003))
        buy_price_ksh = 1200.0
    elif selected_asset == 'AAPL':
        qty = float(request.form.get('qty', 10))
        buy_price_ksh = 200000.0 # e.g. 10 shares at 20k KSh each
    elif selected_asset == 'NVDA':
        qty = float(request.form.get('qty', 5))
        buy_price_ksh = 70000.0
    elif selected_asset == 'gold':
        qty = float(request.form.get('qty', 2))
        buy_price_ksh = 100000.0
    elif selected_asset == 'oil':
        qty = float(request.form.get('qty', 10))
        buy_price_ksh = 150000.0
    else:
        qty = float(request.form.get('qty', 0.0))
        buy_price_ksh = 0.0
    # --- End of hardcoded portfolio values ---

    currency = 'KES'
    
    # Fetch current price based on asset type
    current_price = 0
    if asset_type == 'other':
        current_price = get_market_price(selected_asset, currency) or 0
    elif asset_type == 'stocks':
        # NOTE: Stock price fetching is not implemented. Using a placeholder.
        dummy_stock_prices = {'AAPL': 25000, 'NVDA': 15000}
        current_price = dummy_stock_prices.get(selected_asset, 0)

    # Fallback if API fails
    if current_price == 0 and selected_asset == 'bitcoin':
        current_price = 13000000.0

    total_value = qty * current_price
    profit_loss = total_value - buy_price_ksh 
    
    symbol = SYMBOLS.get(currency, 'KSh')
    now = datetime.now().strftime("%H:%M:%S")

    return render_template('tracker.html', 
                           total_value=total_value,
                           profit_loss=profit_loss,
                           last_updated=now,
                           asset_type=asset_type,
                           assets=assets,
                           selected_asset=selected_asset,
                           qty=qty,
                           symbol=symbol,
                           currency=currency)

if __name__ == '__main__':
    app.run(debug=True)