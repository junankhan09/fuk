from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import os

app = Flask(__name__)


# --- ULTRA SIMPLE CORS FIX - Allow EVERYTHING from your domain ---
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://wondrous-faloodeh-dc7156.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/')
def home():
    return jsonify({"message": "Apex Pulse API is running"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/candles')
def get_candles():
    """Get candle data"""
    try:
        asset = request.args.get('asset', 'EURUSD')
        api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return Response(
                response.content,
                status=200,
                content_type='application/json'
            )
        else:
            return jsonify({"error": f"API returned {response.status_code}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/news')
def get_news():
    """Get news data"""
    try:
        url = "https://alltradingapi.com/prax/server.php/forex_factory/news"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return Response(
                response.content,
                status=200,
                content_type='application/json'
            )
        else:
            return jsonify([])
    except:
        return jsonify([])


# For Vercel deployment
app = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)