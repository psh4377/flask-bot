import os
import discord
from discord.ext import commands
from flask import Flask, request
from dotenv import load_dotenv
import urllib.parse
import threading
import logging
import yt_dlp as youtube_dl

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting application...")

# Flask 앱 설정
app = Flask(__name__)


# 루트 경로 처리 라우트 추가
@app.route('/')
def index():
    return "<h1>Welcome to the Discord Flask Bot Server</h1>"


@app.route('/image')
def image_page():
    try:
        encoded_image_url = request.args.get('full_url', '').strip()
        full_image_url = urllib.parse.unquote(encoded_image_url)
        return f"<html><head><meta property='og:image' content='{full_image_url}'/></head><body><img src='{full_image_url}'/></body></html>"
    except Exception as e:
        logging.error(f"Error in /image route: {e}")
        return "Error", 500


# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PYTHON")
if not DISCORD_TOKEN:
    raise ValueError("Discord token is not set in environment variables!")


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")


# Discord 봇 및 Flask 서버 실행
def run_flask():
    port = int(os.getenv("PORT", 8080))
    logging.info(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)


def run_discord_bot():
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logging.error(f"Error while running Discord bot: {e}")


if __name__ == "__main__":
    # Flask와 Discord 봇을 동시에 실행하기 위해 멀티스레드 사용
    threading.Thread(target=run_flask, daemon=True).start()
    run_discord_bot()
