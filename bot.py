import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import logging
import yt_dlp as youtube_dl
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

# yt-dlp 및 FFmpeg 옵션 설정
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# FFmpeg 실행 파일의 경로를 명시적으로 지정
# FFmpeg 실행 파일의 절대 경로
ffmpeg_options = {
    'before_options':
    ('-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
     '-probesize 32M -analyzeduration 64M'),
    'options':
    '-vn -b:a 256k -af "aresample=async=1:min_hard_comp=0.1:first_pts=0" -ar 48000',
    'executable':
    '/home/runner/flask-bot/ffmpeg-7.0.2-i686-static/ffmpeg'  # 여기에 명확히 경로 지정
}

# 명령어 정의 및 등록


@bot.command(name='play', help='유튜브 링크의 오디오를 스트리밍합니다.')
async def play(ctx, url):
    # 기존의 play 명령어가 있다면 제거
    existing_command = bot.get_command('play')
    if existing_command:
        bot.remove_command('play')

    # play 명령어 로직
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
        data = ytdl.extract_info(url, download=False)
        audio_url = data['url']
        audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        vc.play(audio_source,
                after=lambda e: logging.error(f"Player error: {e}")
                if e else None)
        await ctx.send(f"재생 중: {data['title']}")
    except youtube_dl.utils.DownloadError as e:
        await ctx.send("유효하지 않은 유튜브 링크입니다.")
        logging.error(f"DownloadError: {e}")
    except Exception as e:
        await ctx.send(f"재생 중 오류 발생: {e}")
        logging.error(f"Error during playback: {e}")


@bot.command(name='stop', help='현재 재생 중인 음악을 멈춥니다.')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("음악 재생을 멈췄습니다.")
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")


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

    # Discord 봇 시작
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
