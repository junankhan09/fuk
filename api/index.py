from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# --- CRITICAL: Only these domains can access your API ---
ALLOWED_DOMAINS = [
    'https://wondrous-faloodeh-dc7156.netlify.app',  # MY URL
     # For local testing
    'file://'  # For local file access
]


@app.before_request
def block_unauthorized_domains():
    """Block any request not coming from your allowed domains"""
    # Get where the request came from
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')

    # Allow requests with no origin/referer (like your Vercel backend itself)
    if not origin and not referer:
        return

    # Check if request comes from YOUR domain
    if origin:
        for allowed in ALLOWED_DOMAINS:
            if origin.startswith(allowed):
                return  # Allowed - continue
        # If we get here, origin is not allowed
        print(f"❌ BLOCKED: Request from unauthorized origin: {origin}")
        abort(403, description="Access Denied: Unauthorized Domain")

    # Check referer if origin wasn't present
    if referer:
        for allowed in ALLOWED_DOMAINS:
            if referer.startswith(allowed):
                return  # Allowed - continue
        # If we get here, referer is not allowed
        print(f"❌ BLOCKED: Request from unauthorized referer: {referer}")
        abort(403, description="Access Denied: Unauthorized Domain")


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://alltradingapi.com/'
        }

        response = requests.get(api_url, headers=headers, timeout=10)
        return Response(
            response.content,
            status=response.status_code,
            content_type='application/json'
        )
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({"error": "Could not fetch data"}), 500


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