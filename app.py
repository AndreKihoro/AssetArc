from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_btc_data():
    try:
        # Fetch live BTC price in KES and USD
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=kes,usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['bitcoin']['kes']), float(data['bitcoin']['usd'])
    except Exception:
        return 12800000.0, 97500.0  # Fallbacks

@app.route('/', methods=['GET', 'POST'])
def index():
    # User defaults
    btc_balance = 0.00009644
    buy_price_ksh = 1200.0
    currency = 'KSH'

    if request.method == 'POST':
        btc_balance = float(request.form.get('btc_amount', btc_balance))
        buy_price_ksh = float(request.form.get('buy_price', buy_price_ksh))
        currency = request.form.get('currency', 'KSH')

    price_kes, price_usd = get_btc_data()

    if currency == 'USD':
        current_price = price_usd
        symbol = "$"
        # Calculate USD equivalent of the KES investment
        initial_investment = buy_price_ksh / (price_kes / price_usd)
    else:
        current_price = price_kes
        symbol = "KSh"
        initial_investment = buy_price_ksh

    total_value = btc_balance * current_price
    profit_loss = total_value - initial_investment

    return render_template('index.html', 
                           total_value=total_value, 
                           current_price=current_price, 
                           btc_balance=btc_balance,
                           profit_loss=profit_loss,
                           symbol=symbol,
                           currency=currency,
                           buy_price_ksh=buy_price_ksh)

if __name__ == '__main__':
    app.run(debug=True)