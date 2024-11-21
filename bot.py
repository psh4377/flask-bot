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

# 유튜브 다운로드 옵션
ytdl_format_options = {
    'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '256'}],
    'quiet': True,
    'no_warnings': True,
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# FFmpeg 스트리밍 옵션
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 10M -analyzeduration 20M',
    'options': '-vn -b:a 256k'
}

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 봇 이벤트 및 명령어
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
    if not vc.is_connected():
        await ctx.voice_client.disconnect()
        await channel.connect()

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        audio_source = discord.FFmpegPCMAudio(data['url'], **ffmpeg_options)
        vc.play(audio_source, after=lambda e: print(f"Player error: {e}") if e else None)
        await ctx.send(f"재생 중: {data['title']}")
    except Exception as e:
        await ctx.send(f"재생 중 오류 발생: {e}")

@bot.command(name='stop', help='현재 재생 중인 음악을 멈춥니다.')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("음악 재생을 멈췄습니다.")
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")

@bot.command(name='leave', help='봇이 음성 채널을 떠납니다.')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("음성 채널에서 나갔습니다.")
    else:
        await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")

# Discord 봇 및 Flask 서버 실행
def run_discord_bot():
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        logging.error(f"Error while running Discord bot: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_discord_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
