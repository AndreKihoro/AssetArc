from flask import Flask, render_template, request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

app = Flask(__name__)

# Stability: Prevents "Price 1" glitches by retrying failed API calls
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

SYMBOLS = {'USD': '$', 'KES': 'KSh', 'EUR': '€', 'GBP': '£'}
CRYPTO_ASSETS = {'bitcoin': 'Bitcoin', 'ethereum': 'Ethereum', 'dogecoin': 'Dogecoin'}
STOCK_ASSETS = {'AAPL': 'Apple Inc.', 'NVDA': 'NVIDIA', 'TSLA': 'Tesla'}

def get_market_price(asset_id, currency):
    try:
        # Currently optimized for Crypto. For Stocks, you'd add Alpha Vantage logic here.
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies={currency.lower()}"
        response = session.get(url, timeout=10)
        data = response.json()
        return float(data.get(asset_id, {}).get(currency.lower()))
    except:
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    asset_type = request.args.get('type', 'crypto')
    selected_asset = request.form.get('asset_id', 'bitcoin')
    qty = float(request.form.get('qty', 0.00009644))
    
    # KSEF Context: Your specific initial investment
    buy_price_ksh = 1200.0 
    currency = 'KES'
    
    # Get Market Data with Accurate Fallback
    current_price = get_market_price(selected_asset, currency)
    if not current_price:
        current_price = 13000000.0 if selected_asset == 'bitcoin' else 350000.0
    
    total_value = qty * current_price
    profit_loss = total_value - buy_price_ksh 
    
    symbol = SYMBOLS.get(currency, 'KSh')
    now = datetime.now().strftime("%H:%M:%S")

    return render_template('tracker.html', 
                           total_value=total_value,
                           profit_loss=profit_loss,
                           last_updated=now,
                           asset_type=asset_type,
                           assets=CRYPTO_ASSETS if asset_type == 'crypto' else STOCK_ASSETS,
                           selected_asset=selected_asset,
                           qty=qty,
                           symbol=symbol)

if __name__ == '__main__':
    app.run(debug=True)