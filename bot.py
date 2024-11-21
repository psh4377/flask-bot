import os
import discord
from discord.ext import commands
from flask import Flask, request
import urllib.parse
import asyncio
import threading
import logging
import yt_dlp as youtube_dl

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting application...")

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

ytdl_format_options = {
    'format': 'bestaudio[ext=m4a]/bestaudio',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0'  # IPv6 연결 문제 방지
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0:dither_method=shibata" -b:a 320k'
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

@bot.command(name='play', help='유튜브 링크의 오디오를 재생합니다.')
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("먼저 음성 채널에 들어가야 합니다!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()

    try:
        loop = asyncio.get_event_loop()
        # 유튜브 오디오를 다운로드하여 로컬 파일로 저장
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
        audio_file = ytdl.prepare_filename(data)

        # 로컬 파일로 스트리밍
        audio_source = discord.FFmpegPCMAudio(audio_file, **ffmpeg_options)
        vc.play(audio_source, after=lambda e: logging.error(f"Player error: {e}") if e else None)
        await ctx.send(f"재생 중: {data['title']}")
    except Exception as e:
        await ctx.send(f"재생 중 오류 발생: {e}")
        logging.error(f"Error during playback: {e}")

@bot.command(name='clear', help='지정된 수의 메시지를 삭제합니다.')
async def clear(ctx, count: int = 100):
    try:
        # 입력 값 검증
        if count <= 0 or count > 1000:
            await ctx.send("천 개까지만 지워드려요.")
            return

        # 메시지 삭제 권한 확인
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("권한이 없다고 하네요. 카드는 주고 일하라 하셔야죠…")
            return

        # 메시지 삭제 작업 시작
        deleted = await ctx.channel.purge(limit=count)
        await ctx.send(f"한 {len(deleted)} 마디 정도 지운 것 같은데. 작작 쓰세요.")
    except Exception as e:
        await ctx.send(f"명령 처리 중 오류가 발생했습니다: {e}")
        logging.error(f"Error in !clear command: {e}")


# Discord 봇 및 Flask 서버 실행
def run_discord_bot():
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        logging.error(f"Error while running Discord bot: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_discord_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
