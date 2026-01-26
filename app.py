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
    # 1. Fetch the price (Replace this with your actual API logic)
    # Example using a simple placeholder or your API variable:
    # If your API variable is named something else, change it here!
    price_in_ksh = 12000000  # <--- THIS MUST BE DEFINED FIRST
    
    btc_balance = 0.00009644
    
    # 2. Use the variable we just defined
    current_price_ksh = price_in_ksh 
    total_ksh = btc_balance * current_price_ksh
    
    # 3. Calculate Profit (Since you spent KSh 1200)
    initial_investment = 1200
    profit_loss = total_ksh - initial_investment

    return render_template('index.html', 
                           total_ksh=total_ksh, 
                           current_price_ksh=current_price_ksh, 
                           btc_balance=btc_balance,
                           profit_loss=profit_loss)

if __name__ == '__main__':
    app.run(debug=True)