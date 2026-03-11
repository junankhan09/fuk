from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({"message": "Apex Pulse API is running"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/candles')
def get_candles():
    """Proxy for quotex_candles API - ONLY uses real API, no random data"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        # Build the EXACT same URL your original HTML uses
        api_url = f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"

        # Add headers to mimic a browser EXACTLY like your HTML does
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://alltradingapi.com/',
            'Origin': 'https://alltradingapi.com',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }

        print(f"🔄 Fetching from API: {api_url}")

        # Make the request to the external API
        response = requests.get(api_url, headers=headers, timeout=10)

        print(f"📊 API Response Status: {response.status_code}")

        # If API returns success, return the EXACT data
        if response.status_code == 200:
            print(f"✅ Success! Returning real API data for {asset}")
            return Response(
                response.content,
                status=200,
                content_type='application/json'
            )
        else:
            # API returned error - return error message, NO random data
            print(f"❌ API Error {response.status_code} for {asset}")
            return jsonify({
                "error": f"API returned status {response.status_code}",
                "message": "Unable to fetch real data from API"
            }), 503  # 503 Service Unavailable

    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout error for {asset}")
        return jsonify({
            "error": "API timeout",
            "message": "The external API is not responding"
        }), 504  # 504 Gateway Timeout

    except requests.exceptions.ConnectionError:
        print(f"🔌 Connection error for {asset}")
        return jsonify({
            "error": "Connection error",
            "message": "Cannot connect to external API"
        }), 502  # 502 Bad Gateway

    except Exception as e:
        print(f"💥 Unexpected error for {asset}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/news')
def get_news():
    """Proxy for forex factory news - ONLY uses real API"""
    try:
        url = "https://alltradingapi.com/prax/server.php/forex_factory/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return Response(
                response.content,
                status=200,
                content_type='application/json'
            )
        else:
            return jsonify({
                "error": f"News API returned {response.status_code}"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "error": f"News API error: {str(e)}"
        }), 500


# For Vercel deployment
app = app

if __name__ == '__main__':
    print("🚀 Starting Apex Pulse API Proxy...")
    app.run(host='0.0.0.0', port=5000, debug=True)