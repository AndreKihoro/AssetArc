from flask import Flask, render_template
import requests

# Project: AssetArc
# Author: Andre Kihoro Mugo (GitHub: AndreKihoro)
# Description: A real-time wealth tracking web application.

app = Flask(__name__)

# --- Configuration ---
# Your actual BTC balance
MY_BTC_BALANCE = 0.00009644

def get_live_prices():
    """Fetches live BTC price in KSh and USD using CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'kes,usd'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Check if the request was successful
        data = response.json()
        
        btc_kes = data['bitcoin']['kes']
        btc_usd = data['bitcoin']['usd']
        
        return {
            'price_kes': btc_kes,
            'price_usd': btc_usd,
            'success': True
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {
            'price_kes': 0,
            'price_usd': 0,
            'success': False
        }

@app.route('/')
def index():
    # 1. Fetch live data
    price_data = get_live_prices()
    
    # 2. Calculate your wealth
    my_value_kes = MY_BTC_BALANCE * price_data['price_kes']
    my_value_usd = MY_BTC_BALANCE * price_data['price_usd']
    
    # 3. Render the dashboard with data
    return render_template(
        'index.html', 
        balance=MY_BTC_BALANCE,
        price_kes=price_data['price_kes'],
        price_usd=price_data['price_usd'],
        total_kes=my_value_kes,
        total_usd=my_value_usd,
        status=price_data['success']
    )

if __name__ == '__main__':
    app.run(debug=True)