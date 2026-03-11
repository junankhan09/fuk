from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Allow all origins for now (we'll lock it later)


@app.route('/')
def home():
    return jsonify({"message": "Apex Pulse API is running"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/candles')
def get_candles():
    """Simple proxy for quotex_candles API"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        # Direct API call - exactly like your HTML does
        api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"

        # Simple headers that work
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Make the request with a timeout
        response = requests.get(api_url, headers=headers, timeout=10)

        # Return the exact response
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
    """Simple proxy for news API"""
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