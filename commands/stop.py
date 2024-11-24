from discord.ext import commands
import logging


# stop 명령어 정의
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("음악 재생을 멈췄습니다.")
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")


# setup 함수 정의
def setup(bot):
    if "stop" not in bot.all_commands:
        bot.add_command(
            commands.Command(stop, name="stop", help="현재 재생 중인 음악을 멈춥니다."))
        logging.info("Stop command registered successfully.")
    else:
        logging.warning("Stop command is already registered, skipping.")
