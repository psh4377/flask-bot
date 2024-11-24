from discord.ext import commands
import logging


# leave 명령어 정의
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("음성 채널에서 나갔습니다.")
    else:
        await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")


# setup 함수 정의
def setup(bot):
    if "leave" not in bot.all_commands:
        bot.add_command(
            commands.Command(leave, name="leave", help="봇이 음성 채널을 떠납니다."))
        logging.info("Leave command registered successfully.")
    else:
        logging.warning("Leave command is already registered, skipping.")
