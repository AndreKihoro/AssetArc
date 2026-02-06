from flask import Flask, render_template, request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# Stability: Prevents "Price 1" glitches by retrying failed API calls
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

SYMBOLS = {
    'USD': '$', 'KES': 'KSh', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 
    'INR': '₹', 'ZAR': 'R', 'UGX': 'USh', 'TZS': 'TSh', 'NGN': '₦',
    'GHS': 'GH₵', 'RWF': 'RF', 'CNY': '¥', 'AUD': 'A$', 'CAD': 'C$',
    'CHF': 'Fr', 'BRL': 'R$', 'RUB': '₽', 'SAR': 'SR', 'AED': 'DH'
}

def get_btc_data(target_currency):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={target_currency.lower()}"
        response = session.get(url, timeout=10)
        data = response.json()
        price = data.get('bitcoin', {}).get(target_currency.lower())
        return float(price) if price else None
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    btc_balance = 0.00009644
    buy_price_ksh = 1200.0
    currency = 'KES'

    if request.method == 'POST':
        btc_balance = float(request.form.get('btc_amount', btc_balance))
        buy_price_ksh = float(request.form.get('buy_price', buy_price_ksh))
        currency = request.form.get('currency', 'KES')

    current_price = get_btc_data(currency)
    
    # Accurate Fallbacks
    if current_price is None:
        fallbacks = {'KES': 13000000.0, 'USD': 102000.0}
        current_price = fallbacks.get(currency, 1.0)

    price_in_kes = get_btc_data('KES') or 13000000.0
    conversion_factor = current_price / price_in_kes
    initial_investment_converted = buy_price_ksh * conversion_factor

    total_value = btc_balance * current_price
    profit_loss = total_value - initial_investment_converted
    symbol = SYMBOLS.get(currency, currency + " ")

    return render_template('index.html', 
                           total_value=total_value, 
                           current_price=current_price, 
                           btc_balance=btc_balance,
                           profit_loss=profit_loss,
                           symbol=symbol,
                           currency=currency,
                           buy_price_ksh=buy_price_ksh,
                           currencies=sorted(SYMBOLS.keys()))

if __name__ == '__main__':
    app.run(debug=True)