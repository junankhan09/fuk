from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import time

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


@app.route('/api/candles')
def get_candles():
    """Get candle data from external API"""
    try:
        asset = request.args.get('asset', 'EURUSD')

        print("=" * 50)
        print(f"🔍 Getting data for: {asset}")
        print("=" * 50)

        # Get ALL URLs from environment variables (COMPLETELY HIDDEN)
        urls_to_try = [
            os.getenv('QUOTEX_API_URL_1', f"https://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"),
            os.getenv('QUOTEX_API_URL_2', f"http://alltradingapi.com/prax/server.php/quotex_candles?asset={asset}"),
            os.getenv('QUOTEX_API_URL_3', f"https://alltradingapi.com/prax/quotex_candles?asset={asset}")
        ]

        # Headers that mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://alltradingapi.com/',
            'Origin': 'https://alltradingapi.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Try each URL
        for i, url in enumerate(urls_to_try, 1):
            print(f"\n📡 Attempt {i}: Trying {url}")

            try:
                # Create a session (like a browser tab)
                session = requests.Session()

                # First visit the main site (like opening the website)
                print("   Visiting main site first...")
                session.get('https://alltradingapi.com', headers=headers, timeout=5)

                # Then ask for the data
                print("   Requesting data...")
                response = session.get(url, headers=headers, timeout=10)

                print(f"   Response status: {response.status_code}")

                if response.status_code == 200:
                    print(f"✅ SUCCESS with URL {i}!")
                    data = response.json()
                    print(f"   Got {len(data)} candles")
                    return jsonify(data)
                else:
                    print(f"❌ Failed with status {response.status_code}")

            except Exception as e:
                print(f"❌ Attempt {i} error: {str(e)[:100]}")  # Show first 100 chars
                continue

        # If all attempts fail, return sample data
        print("\n⚠️ All attempts failed, using sample data")
        sample_data = get_sample_data()
        return jsonify(sample_data)

    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/news')
def get_news():
    """Get news data"""
    try:
        url = "https://alltradingapi.com/prax/server.php/forex_factory/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify([])
    except:
        return jsonify([])


def get_sample_data():
    """Return sample data when API is down"""
    return [
        {"open": "1.0582", "close": "1.0597", "high": "1.0601", "low": "1.0578", "direction": "CALL"},
        {"open": "1.0575", "close": "1.0582", "high": "1.0585", "low": "1.0570", "direction": "CALL"},
        {"open": "1.0568", "close": "1.0575", "high": "1.0579", "low": "1.0562", "direction": "CALL"},
        {"open": "1.0559", "close": "1.0568", "high": "1.0570", "low": "1.0555", "direction": "CALL"},
        {"open": "1.0550", "close": "1.0559", "high": "1.0562", "low": "1.0548", "direction": "CALL"}
    ]


if __name__ == '__main__':
    print("🚀 Starting Apex Pulse Backend with Sample Data Fallback...")
    app.run(host='0.0.0.0', port=5000, debug=True)

    # For Vercel deployment
    app = app