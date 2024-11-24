from discord.ext import commands
import yt_dlp as youtube_dl
import discord
import logging

# yt-dlp 및 FFmpeg 옵션 설정
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'before_options': (
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-probesize 32M -analyzeduration 64M'
    ),
    'options': '-vn -b:a 256k -af "aresample=async=1:min_hard_comp=0.1:first_pts=0" -ar 48000'
}

# setup 함수 정의
def setup(bot):
    @bot.command(name='play', help='유튜브 링크의 오디오를 스트리밍합니다.')
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
            data = ytdl.extract_info(url, download=False)
            audio_url = data['url']
            audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            vc.play(audio_source, after=lambda e: logging.error(f"Player error: {e}") if e else None)
            await ctx.send(f"재생 중: {data['title']}")
        except youtube_dl.utils.DownloadError as e:
            await ctx.send("유효하지 않은 유튜브 링크입니다.")
            logging.error(f"DownloadError: {e}")
        except Exception as e:
            await ctx.send(f"재생 중 오류 발생: {e}")
            logging.error(f"Error during playback: {e}")
