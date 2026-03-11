from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)


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
    """Get candle data for any pair"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        # Try external API first
        try:
            api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(api_url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return jsonify(data)
        except:
            pass

        # Generate accurate sample data based on asset type
        return jsonify(generate_candles_for_asset(asset))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/news')
def get_news():
    """Get sample news"""
    news = [
        {"title": "Market update: Trading volumes normal", "time": "1h ago"},
        {"title": "Technical analysis suggests range-bound movement", "time": "2h ago"},
        {"title": "Major pairs show consolidation pattern", "time": "3h ago"}
    ]
    return jsonify(news)


def get_asset_info(asset):
    """Determine asset type and return appropriate pricing info"""

    # Default for Forex majors
    info = {
        'base_price': 1.0500,
        'decimals': 5,
        'spread': 0.0010,
        'volatility': 0.3,
        'type': 'forex'
    }

    # Forex pairs (Real Market)
    if asset in ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD']:
        info['base_price'] = 1.0500
        info['decimals'] = 5
        info['spread'] = 0.0010
    elif asset in ['USDJPY', 'EURJPY', 'GBPJPY', 'AUDJPY', 'CADJPY', 'CHFJPY', 'NZDJPY']:
        info['base_price'] = 150.00
        info['decimals'] = 3
        info['spread'] = 0.10
    elif asset in ['USDCHF', 'EURCHF', 'GBPCHF', 'NZDCHF']:
        info['base_price'] = 0.9000
        info['decimals'] = 5
        info['spread'] = 0.0008
    elif asset in ['USDCAD', 'EURCAD', 'GBPCAD', 'AUDCAD', 'NZDCAD']:
        info['base_price'] = 1.3500
        info['decimals'] = 5
        info['spread'] = 0.0012
    elif asset in ['AUDNZD', 'EURNZD', 'GBPNZD']:
        info['base_price'] = 1.1000
        info['decimals'] = 5
        info['spread'] = 0.0015
    elif asset in ['EURGBP', 'EURAUD', 'GBPAUD']:
        info['base_price'] = 0.8500
        info['decimals'] = 5
        info['spread'] = 0.0009

    # OTC Forex pairs (similar but with slight variation)
    elif asset.endswith('_otc') and not any(crypto in asset for crypto in ['BTC', 'ETH', 'XRP', 'SOL']):
        base_asset = asset.replace('_otc', '')
        if base_asset in ['EURUSD', 'GBPUSD', 'AUDUSD']:
            info['base_price'] = 1.0520
        elif base_asset in ['USDJPY', 'EURJPY']:
            info['base_price'] = 150.20
        elif base_asset in ['GBPJPY']:
            info['base_price'] = 187.50
        else:
            info['base_price'] = 1.1000
        info['decimals'] = 5
        info['spread'] = 0.0015
        info['type'] = 'forex_otc'

    # Commodities
    elif asset in ['XAUUSD', 'XAUUSD_otc', 'Gold']:
        info['base_price'] = 2000.00
        info['decimals'] = 2
        info['spread'] = 1.50
        info['volatility'] = 0.8
        info['type'] = 'commodity'
    elif asset in ['XAGUSD', 'XAGUSD_otc', 'Silver']:
        info['base_price'] = 25.00
        info['decimals'] = 3
        info['spread'] = 0.20
        info['volatility'] = 0.7
        info['type'] = 'commodity'
    elif asset in ['XBRUSD', 'XTIUSD', 'UKBrent_otc', 'USCrude_otc', 'Brent Oil', 'WTI Oil']:
        info['base_price'] = 80.00
        info['decimals'] = 2
        info['spread'] = 0.50
        info['volatility'] = 1.2
        info['type'] = 'commodity'
    elif asset in ['NATGAS', 'Natural Gas']:
        info['base_price'] = 2.50
        info['decimals'] = 3
        info['spread'] = 0.05
        info['volatility'] = 1.5
        info['type'] = 'commodity'

    # Cryptocurrencies
    elif 'BTC' in asset:
        info['base_price'] = 65000.00
        info['decimals'] = 2
        info['spread'] = 150.00
        info['volatility'] = 2.0
        info['type'] = 'crypto'
    elif 'ETH' in asset:
        info['base_price'] = 3500.00
        info['decimals'] = 2
        info['spread'] = 20.00
        info['volatility'] = 1.8
        info['type'] = 'crypto'
    elif 'SOL' in asset:
        info['base_price'] = 140.00
        info['decimals'] = 3
        info['spread'] = 2.00
        info['volatility'] = 2.2
        info['type'] = 'crypto'
    elif 'XRP' in asset:
        info['base_price'] = 0.60
        info['decimals'] = 4
        info['spread'] = 0.01
        info['volatility'] = 2.5
        info['type'] = 'crypto'
    elif 'ADA' in asset:
        info['base_price'] = 0.40
        info['decimals'] = 4
        info['spread'] = 0.01
        info['volatility'] = 2.3
        info['type'] = 'crypto'
    elif 'DOGE' in asset or 'DOG' in asset:
        info['base_price'] = 0.15
        info['decimals'] = 4
        info['spread'] = 0.005
        info['volatility'] = 3.0
        info['type'] = 'crypto'
    elif 'SHIB' in asset or 'SHI' in asset:
        info['base_price'] = 0.000025
        info['decimals'] = 8
        info['spread'] = 0.000001
        info['volatility'] = 3.5
        info['type'] = 'crypto'
    elif 'BNB' in asset:
        info['base_price'] = 550.00
        info['decimals'] = 2
        info['spread'] = 5.00
        info['volatility'] = 1.5
        info['type'] = 'crypto'
    elif 'LTC' in asset:
        info['base_price'] = 80.00
        info['decimals'] = 2
        info['spread'] = 1.00
        info['volatility'] = 1.6
        info['type'] = 'crypto'
    elif 'DOT' in asset:
        info['base_price'] = 7.50
        info['decimals'] = 3
        info['spread'] = 0.10
        info['volatility'] = 2.0
        info['type'] = 'crypto'
    elif 'LINK' in asset or 'LIN' in asset:
        info['base_price'] = 15.00
        info['decimals'] = 3
        info['spread'] = 0.20
        info['volatility'] = 2.2
        info['type'] = 'crypto'

    # Stocks
    elif any(stock in asset for stock in
             ['MSFT', 'AAPL', 'GOOG', 'META', 'AMZN', 'TSLA', 'NFLX', 'NVDA', 'MCD', 'JNJ', 'PFE', 'BA', 'INTC', 'AXP',
              'FB']):
        stock_prices = {
            'MSFT': 400.00, 'AAPL': 175.00, 'GOOG': 140.00, 'META': 470.00,
            'AMZN': 175.00, 'TSLA': 180.00, 'NFLX': 600.00, 'NVDA': 900.00,
            'MCD': 280.00, 'JNJ': 160.00, 'PFE': 28.00, 'BA': 180.00,
            'INTC': 42.00, 'AXP': 230.00, 'FB': 470.00
        }
        for stock, price in stock_prices.items():
            if stock in asset:
                info['base_price'] = price
                break
        info['decimals'] = 2
        info['spread'] = 1.00
        info['volatility'] = 1.0
        info['type'] = 'stock'

    return info


def generate_candles_for_asset(asset):
    """Generate realistic candles for any asset"""

    # Get asset info
    info = get_asset_info(asset)
    base_price = info['base_price']
    decimals = info['decimals']
    spread = info['spread']
    volatility = info.get('volatility', 0.5)

    # Use time to create variation (changes every 2 minutes)
    seed = int(time.time() / 120) + hash(asset) % 10000
    random.seed(seed)

    # Generate trend direction (changes every 30 minutes)
    trend_seed = int(time.time() / 1800)
    random.seed(trend_seed + hash(asset) % 10000)
    trend = random.choice([-1, -0.5, 0, 0.5, 1])

    candles = []
    current_price = base_price + random.uniform(-spread, spread)

    for i in range(20):
        # Calculate price change with trend
        change_percent = random.uniform(-volatility, volatility) / 100
        trend_factor = trend * 0.0002
        change = current_price * change_percent + trend_factor

        # Open = previous close
        open_price = current_price
        close_price = open_price + change

        # Ensure price doesn't go negative
        close_price = max(close_price, base_price * 0.5)

        # Generate realistic high and low
        price_range = abs(change) * random.uniform(1.5, 3.0)
        high_price = max(open_price, close_price) + price_range
        low_price = min(open_price, close_price) - price_range * 0.7

        # Ensure low is reasonable
        low_price = max(low_price, base_price * 0.4)

        # Determine direction
        if close_price > open_price * 1.0001:
            direction = "CALL"
        elif close_price < open_price * 0.9999:
            direction = "PUT"
        else:
            direction = "NEUTRAL"

        # Format with correct decimal places
        candles.append({
            "open": f"{open_price:.{decimals}f}",
            "close": f"{close_price:.{decimals}f}",
            "high": f"{high_price:.{decimals}f}",
            "low": f"{low_price:.{decimals}f}",
            "direction": direction
        })

        # Update for next candle
        current_price = close_price

    return candles


# CRITICAL for Vercel
app = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)