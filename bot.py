import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import logging
from flask_app import run_flask  # flask_app 모듈에서 Flask 실행 함수 임포트

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting application...")

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# DISCORD_TOKEN을 환경 변수에서 가져오기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PYTHON")

if not DISCORD_TOKEN:
    raise ValueError("Discord token is not set in environment variables!")

# 명령어 모듈 임포트
from commands.play import setup as setup_play
from commands.clear import setup as setup_clear

# 봇에 명령어 등록
setup_play(bot)
setup_clear(bot)

# 봇의 이벤트 정의
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

# 비동기 main 함수
async def main():
    loop = asyncio.get_running_loop()
    loop.create_task(bot.start(DISCORD_TOKEN))  # Discord 봇 시작
    run_flask()  # Flask 서버 실행

if __name__ == "__main__":
    asyncio.run(main())
