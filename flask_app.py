from flask import Flask, request
import urllib.parse
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# Flask 앱 설정
app = Flask(__name__)

@app.route('/image')
def image_page():
    try:
        encoded_image_url = request.args.get('full_url', '').strip()
        full_image_url = urllib.parse.unquote(encoded_image_url)
        return f"<html><head><meta property='og:image' content='{full_image_url}'/></head><body><img src='{full_image_url}'/></body></html>"
    except Exception as e:
        logging.error(f"Error in /image route: {e}")
        return "Error", 500

# Flask 앱 실행 함수
def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
