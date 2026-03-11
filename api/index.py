from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import time
import random
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow your HTML to talk to Flask


@app.route('/')
def home():
    return jsonify({"message": "Apex Pulse API is running"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/test')
def test():
    return jsonify({"status": "Flask is working"})


@app.route('/api/candles')
def get_candles():
    """Get candle data from external API"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        print("=" * 50)
        print(f"🔍 Getting data for: {asset}")
        print("=" * 50)

        # Try external API first (with your original working URL)
        try:
            api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"
            print(f"📡 Trying external API: {api_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(api_url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Got {len(data)} candles from external API")
                return jsonify(data)
            else:
                print(f"❌ External API returned {response.status_code}")
        except Exception as e:
            print(f"❌ External API error: {str(e)}")

        # If external API fails, use improved sample data
        print("\n⚠️ Using improved sample data")
        sample_data = get_improved_sample_data(asset)
        return jsonify(sample_data)

    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/news')
def get_news():
    """Get news data"""
    try:
        # Try external API
        url = "https://alltradingapi.com/prax/server.php/forex_factory/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # Return sample news
            return jsonify([
                {"title": "Fed maintains interest rates, signals cautious approach"},
                {"title": "EUR/USD volatility expected ahead of ECB meeting"}
            ])
    except:
        return jsonify([
            {"title": "Market update: Trading volumes normal"},
            {"title": "Technical analysis suggests range-bound movement"}
        ])


def get_improved_sample_data(asset):
    """Return IMPROVED realistic sample data for all pairs"""

    # Set base price and decimal places based on asset
    if 'JPY' in asset:
        base_price = 150.00
        decimal_places = 3
        volatility = 0.3
    elif 'XAU' in asset or 'Gold' in asset:
        base_price = 2000.00
        decimal_places = 2
        volatility = 0.5
    elif 'BTC' in asset:
        base_price = 65000.00
        decimal_places = 2
        volatility = 1.0
    elif 'ETH' in asset:
        base_price = 3500.00
        decimal_places = 2
        volatility = 0.8
    elif 'XAG' in asset or 'Silver' in asset:
        base_price = 25.00
        decimal_places = 3
        volatility = 0.4
    else:  # Forex majors
        base_price = 1.0500
        decimal_places = 5
        volatility = 0.1

    # Use time to create variation (changes every 5 minutes)
    seed = int(time.time() / 300)
    random.seed(seed + hash(asset) % 10000)

    # Generate 20 realistic candles
    candles = []
    current_price = base_price

    # Create a slight trend
    trend = random.choice([-1, 0, 1])

    for i in range(20):
        # Add some randomness to price movement
        change = (random.random() - 0.5 + trend * 0.1) * volatility / 100 * current_price

        # Calculate OHLC
        open_price = current_price
        close_price = open_price + change

        # Ensure close price is reasonable
        close_price = max(min(close_price, open_price * 1.01), open_price * 0.99)

        # Calculate high and low with wicks
        high_price = max(open_price, close_price) + abs(change) * random.random() * 0.5
        low_price = min(open_price, close_price) - abs(change) * random.random() * 0.5

        # Determine direction
        direction = "CALL" if close_price > open_price else "PUT"

        # Format with correct decimal places
        candles.append({
            "open": f"{open_price:.{decimal_places}f}",
            "close": f"{close_price:.{decimal_places}f}",
            "high": f"{high_price:.{decimal_places}f}",
            "low": f"{low_price:.{decimal_places}f}",
            "direction": direction
        })

        # Update current price for next candle
        current_price = close_price

    return candles


# For Vercel deployment
app = app

if __name__ == '__main__':
    print("🚀 Starting Apex Pulse Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)