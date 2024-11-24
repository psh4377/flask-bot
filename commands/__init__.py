# commands/__init__.py
import sys
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import logging
import importlib
import threading
from flask_app import run_flask  # flask_app 모듈에서 Flask 실행 함수 임포트
# 환경 변수 로드
load_dotenv()
# 로깅 설정
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting application...")
# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
# DISCORD_TOKEN을 환경 변수에서 가져오기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PYTHON")
if not DISCORD_TOKEN:
    raise ValueError("Discord token is not set in environment variables!")
# 모든 명령어 파일들을 명시적으로 등록
from commands.play import setup as setup_play
from commands.clear import setup as setup_clear
from commands.stop import setup as setup_stop
from commands.leave import setup as setup_leave
# 각각의 명령어 파일의 setup 호출
setup_play(bot)
setup_clear(bot)
setup_stop(bot)
setup_leave(bot)
# 등록된 명령어 출력 (디버깅용)
logging.info(f"Registered commands at startup: {list(bot.commands)}")


# 봇의 이벤트 정의
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    logging.info(f"Registered commands after on_ready: {list(bot.commands)}")


# 비동기 main 함수
async def main():
    # Flask 서버를 별도의 스레드에서 실행
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    # Discord 봇을 별도의 스레드에서 실행
    discord_thread = threading.Thread(target=bot.run, args=(DISCORD_TOKEN, ))
    discord_thread.daemon = True
    discord_thread.start()
    # 메인 스레드에서 대기 (Flask 서버와 Discord 봇이 계속 실행되도록)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
