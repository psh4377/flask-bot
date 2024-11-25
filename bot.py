import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import logging
from yt_dlp import YoutubeDL  # 수정된 부분
import threading
from flask_app import run_flask  # Flask 실행 함수 임포트

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

# DISCORD_TOKEN 환경 변수 가져오기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_PYTHON")
if not DISCORD_TOKEN:
    raise ValueError("Discord token is not set in environment variables!")

# yt-dlp 및 FFmpeg 옵션 설정
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # IPv4
}

ffmpeg_options = {
    'before_options':
    ('-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
     '-probesize 32M -analyzeduration 64M'),
    'options':
    '-vn -b:a 256k -af "aresample=async=1:min_hard_comp=0.1:first_pts=0" -ar 48000',
    'executable':
    'Z:/DiscordBot/ffmpeg-7.0.2-i686-static/ffmpeg'  # 여기에 명확히 경로 지정
}

ytdl = YoutubeDL(ytdl_format_options)  # 수정된 부분


def get_stream_url(youtube_url):
    try:
        info = ytdl.extract_info(youtube_url, download=False)
        stream_url = info['url']
        logging.info(f"Extracted stream URL: {stream_url}")
        return stream_url
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Error extracting stream URL: {e}")
        return None


# 명령어 정의 및 등록
@bot.command(name='play', help='유튜브 링크의 오디오를 스트리밍합니다.')
async def play(ctx, url):
    """유튜브 링크의 오디오를 스트리밍"""
    if not ctx.author.voice:
        await ctx.send("먼저 음성 채널에 들어가야 합니다!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        try:
            await channel.connect()
        except discord.ClientException as e:
            await ctx.send("봇이 이미 다른 채널에 연결되어 있습니다.")
            logging.error(f"Error connecting to voice channel: {e}")
            return

    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()

    # Stream URL 가져오기
    try:
        logging.info("Getting stream URL...")
        stream_url = get_stream_url(url)
        if not stream_url:
            raise ValueError("Stream URL is None or invalid.")
        logging.info(f"Stream URL: {stream_url}")
    except Exception as e:
        logging.error(f"Failed to extract stream URL: {e}")
        await ctx.send("유효하지 않은 유튜브 링크입니다.")
        return

    # FFMPEG Audio 재생
    try:
        logging.info("Initializing FFmpegPCMAudio...")
        audio_source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
        logging.info("Playing audio...")
        vc.play(audio_source,
                after=lambda e: logging.error(f"Player error: {e}")
                if e else None)
        await ctx.send(f"재생 중: {url}")
    except discord.ClientException as e:
        logging.error(f"Discord client error: {e}")
        await ctx.send("디스코드 봇이 음성 채널에서 재생 중 문제가 발생했습니다.")
    except Exception as e:
        logging.error(f"General playback error: {e}")
        await ctx.send("재생 중 알 수 없는 문제가 발생했습니다.")


@bot.command(name='stop', help='현재 재생 중인 음악을 멈춥니다.')
async def stop(ctx):
    """현재 재생 중인 음악 멈추기"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("음악 재생을 멈췄습니다.")
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")


@bot.command(name='clear', help='지정된 수의 메시지를 삭제합니다.')
async def clear(ctx, count: int = 100):
    """지정된 수의 메시지 삭제"""
    try:
        if count <= 0 or count > 1000:
            await ctx.send("천 개까지만 삭제할 수 있습니다.")
            return

        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send("메시지 관리 권한이 없습니다.")
            return

        deleted = await ctx.channel.purge(limit=count)
        await ctx.send(f"{len(deleted)}개의 메시지를 삭제했습니다.")
    except Exception as e:
        await ctx.send("메시지 삭제 중 오류가 발생했습니다.")
        logging.error(f"Error in !clear command: {e}")


@bot.command(name='leave', help='봇이 음성 채널을 떠납니다.')
async def leave(ctx):
    """음성 채널에서 봇 나가기"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("음성 채널에서 나갔습니다.")
    else:
        await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")


# 봇의 이벤트 정의
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    logging.info(f"Registered commands: {list(bot.commands)}")


# 비동기 main 함수
async def main():
    """Flask와 Discord 봇 실행"""
    # Flask 서버를 별도의 스레드에서 실행
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Discord 봇 시작
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
