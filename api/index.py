from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import time
import random

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
    """Get candle data"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        # Try external API first
        try:
            api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(api_url, headers=headers, timeout=5)

            if response.status_code == 200:
                return jsonify(response.json())
        except:
            pass  # Fall back to sample data

        # Return sample data
        return jsonify(get_sample_data(asset))

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


def get_sample_data(asset):
    """Simple sample data that always works"""
    # Basic sample data that works for any asset
    return [
        {"open": "1.0582", "close": "1.0597", "high": "1.0601", "low": "1.0578", "direction": "CALL"},
        {"open": "1.0575", "close": "1.0582", "high": "1.0585", "low": "1.0570", "direction": "CALL"},
        {"open": "1.0568", "close": "1.0575", "high": "1.0579", "low": "1.0562", "direction": "CALL"},
        {"open": "1.0559", "close": "1.0568", "high": "1.0570", "low": "1.0555", "direction": "CALL"},
        {"open": "1.0550", "close": "1.0559", "high": "1.0562", "low": "1.0548", "direction": "CALL"}
    ]


# CRITICAL for Vercel - MUST be at the bottom!
app = app

# This is only for local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)