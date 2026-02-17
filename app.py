from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import random
import os
import sys
import redis
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------
# CONFIGURATION
# -------------------------------
SYMBOLS = {
    "USD": "$",
    "KES": "KSh",
    "EUR": "€",
    "GBP": "£"
}

CRYPTO_ASSETS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "dogecoin": "Dogecoin"
}

# -------------------------------
# REDIS CLIENT
# -------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

# -------------------------------
# SCHEDULER
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_crypto_prices():
    """
    Fetches prices for all configured crypto assets from the CoinGecko API
    and caches them in Redis.
    """
    logger.info("Scheduler: Running scheduled price update...")

    try:
        redis_client.ping()
    except redis.exceptions.ConnectionError:
        logger.warning("Scheduler: Could not connect to Redis. Skipping price update.")
        return

    if not CRYPTO_ASSETS:
        return

    asset_ids = ",".join(CRYPTO_ASSETS.keys())
    currency = "kes"

    try:
        url = (
            f"https://api.coingecko.com/api/v3/simple/price"
            f"?ids={asset_ids}&vs_currencies={currency}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        for asset_id, price_data in data.items():
            if currency in price_data:
                price = float(price_data[currency])
                redis_client.set(f"price:{asset_id}", price, ex=300)
                logger.info(f"Scheduler: Cached price for {asset_id}: {price}")

    except Exception as e:
        logger.error(f"Scheduler: Error updating prices: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=update_crypto_prices, trigger="interval", minutes=5, id="price_update_job")
    scheduler.start()
    logger.info("Scheduler: Started.")

app = Flask(__name__)

# Start scheduler (runs every 5 minutes)
start_scheduler()


# -------------------------------
# PRICE FETCHING WITH CACHE
# -------------------------------
def get_market_price(asset_id, currency="kes"):
    """
    Fetches the market price for a given asset. It first tries to get the price
    from the Redis cache. If Redis is unavailable or the price is not cached,
    it falls back to a live API call and attempts to cache the new price.
    """
    try:
        # Try Redis cache first
        cached_price = redis_client.get(f"price:{asset_id}")
        if cached_price:
            return float(cached_price)
    except redis.exceptions.ConnectionError:
        app.logger.warning("Redis connection failed. Falling back to live API.")
        # Fall through to the API call below

    # Fallback to live API call
    try:
        url = (
            f"https://api.coingecko.com/api/v3/simple/price"
            f"?ids={asset_id}&vs_currencies={currency}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        price = float(data.get(asset_id, {}).get(currency, 0))

        # Try to cache the new price, but don't fail if Redis is down
        try:
            redis_client.set(f"price:{asset_id}", price, ex=300)
        except redis.exceptions.ConnectionError:
            pass  # Silently ignore if we can't cache
        return price
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        app.logger.error(f"API call or data parsing failed for {asset_id}: {e}")
        return 0


# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -------------------------------
# TRACKER PAGE
# -------------------------------
@app.route("/tracker", methods=["GET", "POST"])
def tracker():
    asset_type = request.args.get("type", "crypto")
    selected_asset = request.args.get("asset", "bitcoin")

    # Default currency settings
    currency_code = "KES"
    symbol = SYMBOLS.get(currency_code, "KSh")

    if asset_type == "stocks":
        # Mock price for stocks (consistent with stock_chart_data)
        # since we don't have a live stock API configured.
        current_price = random.uniform(150, 250)
    else:
        current_price = get_market_price(selected_asset, currency_code.lower())

    # Calculate total value (assuming quantity of 1 for display)
    total_value = current_price

    # Mock profit/loss for display purposes (since no purchase history exists)
    profit_loss = total_value * random.uniform(-0.05, 0.05)

    return render_template(
        "tracker.html",
        current_price=current_price,
        assets=CRYPTO_ASSETS,
        selected_asset=selected_asset,
        total_value=total_value,
        symbol=symbol,
        profit_loss=profit_loss
    )


# -------------------------------
# CRYPTO CHART DATA (HOME PAGE)
# -------------------------------
@app.route("/chart-data/crypto/<asset_id>")
def crypto_chart_data(asset_id):
    try:
        url = (
            f"https://api.coingecko.com/api/v3/coins/"
            f"{asset_id}/market_chart?vs_currency=usd&days=30"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        prices = data.get("prices", [])
        return jsonify({"prices": prices})

    except Exception:
        return jsonify({"prices": []})


# -------------------------------
# STOCK CHART DATA (DUMMY DATA)
# -------------------------------
@app.route("/chart-data/stock/<symbol>")
def stock_chart_data(symbol):
    prices = []
    price = random.uniform(150, 200)
    now = datetime.now()

    for i in range(30):
        timestamp = (
            now - timedelta(days=29 - i)
        ).timestamp() * 1000

        price *= random.uniform(0.98, 1.02)
        prices.append([timestamp, price])

    return jsonify({"prices": prices})


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
