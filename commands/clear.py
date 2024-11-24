from discord.ext import commands
import logging

# setup 함수 정의
def setup(bot):
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
