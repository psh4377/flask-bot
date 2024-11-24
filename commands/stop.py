from discord.ext import commands

# setup 함수 정의
def setup(bot):
    @bot.command(name='stop', help='현재 재생 중인 음악을 멈춥니다.')
    async def stop(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("음악 재생을 멈췄습니다.")
        else:
            await ctx.send("현재 재생 중인 음악이 없습니다.")
