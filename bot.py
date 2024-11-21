import os
import discord
from discord.ext import commands
from flask import Flask, render_template_string, request
import urllib.parse
import asyncio
import threading
import logging
import yt_dlp as youtube_dl
import os
import subprocess
try:
    import yt_dlp
except ImportError:
    subprocess.check_call(["pip", "install", "yt-dlp"])
    import yt_dlp

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

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# !on_ready 이벤트
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

# !image 명령어 처리
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!image'):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    logging.info(f"Initial Attachment URL: {attachment.url}")
                    await asyncio.sleep(5)
                    encoded_url = urllib.parse.quote(attachment.url, safe='')
                    page_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/image?full_url={encoded_url}"
                    await message.channel.send(f"이런 것도 혼자 못 하시나요...: {page_url}")
        else:
            await message.channel.send("이미지가 없잖아요. 사진 올리는 거 잊었어요?")
        return

    await bot.process_commands(message)

# !clear 명령어 처리
@bot.command(name='clear', help='지정된 수의 메시지를 삭제합니다.')
async def clear(ctx, count: int = 100):
    if count <= 0 or count > 1000:
        await ctx.send("천 개까지만 지워드려요.")
        return

    if not ctx.channel.permissions_for(ctx.author).manage_messages:
        await ctx.send("권한이 없다고 하네요. 카드는 주고 일하라 하셔야죠…")
        return

    await ctx.send(f"지우는 중이니까 좀 기다려요. ({count}개 메시지)")
    deleted = await ctx.channel.purge(limit=count)
    await ctx.send(f"한 {len(deleted)} 마디 정도 지운 것 같은데. 작작 쓰세요.")

# 유튜브 다운로드 옵션
ytdl_format_options = {
    'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',  # 오디오 품질 256kbps
    }],
    'quiet': True,
    'no_warnings': True,
}

ffmpeg_options = {
    'options': '-vn -b:a 256k'  # 스트리밍 품질 256kbps
}


# !play 명령어
@bot.command(name='play', help='유튜브 링크의 오디오를 재생합니다.')
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("먼저 음성 채널에 들어가야 합니다!")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await channel.connect()

    vc = ctx.voice_client
    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        audio_source = discord.FFmpegPCMAudio(data['url'], **ffmpeg_options)
        vc.play(audio_source, after=lambda e: logging.error(f"Player error: {e}") if e else None)
        await ctx.send(f"재생 중: {data['title']}")
    except Exception as e:
        await ctx.send(f"재생 중 오류 발생: {e}")

# !leave 명령어
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
    # Flask와 봇 실행
    threading.Thread(target=run_discord_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
