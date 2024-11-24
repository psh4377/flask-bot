from discord.ext import commands

# setup 함수 정의
def setup(bot):
    @bot.command(name='leave', help='봇이 음성 채널을 떠납니다.')
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("음성 채널에서 나갔습니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
