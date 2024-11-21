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

# yt-dlp 및 FFmpeg 옵션 설정
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '0',  # 무손실 품질
    }],
    'quiet': True,
    'no_warnings': True,
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -c:a libopus -b:a 128k'
}


# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # '!image' 명령어 처리
    if message.content.startswith('!image'):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    encoded_url = urllib.parse.quote(attachment.url, safe='')
                    page_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/image?full_url={encoded_url}"
                    await message.channel.send(f"이런 것도 혼자 못 하시나요...: {page_url}")
        else:
            await message.channel.send("이미지가 없잖아요. 사진 올리는 거 잊었어요?")
        return

    await bot.process_commands(message)

@bot.command(name='clear', help='지정된 수의 메시지를 삭제합니다.')
async def clear(ctx, count: int = 100):
    try:
        if count <= 0 or count > 1000:
            await ctx.send("천 개까지만 지워드려요.")
            return

        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("권한이 없다고 하네요. 카드는 주고 일하라 하셔야죠…")
            return

        deleted = await ctx.channel.purge(limit=count)
        await ctx.send(f"한 {len(deleted)} 마디 정도 지운 것 같은데. 작작 쓰세요.")
    except Exception as e:
        await ctx.send(f"명령 처리 중 오류가 발생했습니다: {e}")
        logging.error(f"Error in !clear command: {e}")

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
