import os
import discord
from flask import Flask, render_template_string, request
import urllib.parse
import asyncio
import threading
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting application...")

# Flask 앱 설정
app = Flask(__name__)

@app.route('/image')
def image_page():
    try:
        # 요청받은 URL 가져오기
        encoded_image_url = request.args.get('full_url', '').strip()
        logging.info(f"Encoded image URL received: {encoded_image_url}")

        # URL 디코딩
        full_image_url = urllib.parse.unquote(encoded_image_url)
        logging.info(f"Full image URL after decoding: {full_image_url}")

        # HTML 템플릿 생성
        html_template = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta property="og:title" content="Shared Image" />
            <meta property="og:description" content="This image was uploaded via Discord." />
            <meta property="og:image" content="{full_image_url}" />
            <meta property="og:type" content="website" />
            <meta property="og:url" content="{request.url}" />
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content="Shared Image" />
            <meta name="twitter:description" content="This image was uploaded via Discord." />
            <meta name="twitter:image" content="{full_image_url}" />
            
        </head>
        <body>
            <h1>Shared Image</h1>
            <img src="{full_image_url}" alt="Shared Image" />
        </body>
        </html>
        """
        logging.info("HTML template successfully generated.")
        return html_template
    except Exception as e:
        # 오류 발생 시 로그 출력 및 에러 반환
        logging.error(f"Error in /image route: {e}")
        return "An error occurred while processing your request.", 500



# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # 봇 자신의 메시지는 무시
    if message.author == client.user:
        return

    # '!clear' 명령어 처리
    if message.content.startswith('!clear'):
        # 채널 권한 확인
        if not message.channel.permissions_for(message.author).manage_messages:
            await message.channel.send("권한이 없다고 하네요. 카드는 주고 일하라 하셔야죠…")
            return

        # 메시지 삭제 작업 시작
        await message.channel.send("지우는 중이니까 좀 기다려요.")
        deleted = await message.channel.purge(limit=100)  # 최근 100개의 메시지 삭제
        await message.channel.send(f"한 {len(deleted)} 마디 정도 지운 것 같은데. 작작 쓰세요.")
        return

    # 이미지 업로드 처리
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                logging.info(f"Initial Attachment URL: {attachment.url}")
                await asyncio.sleep(5)
                logging.info(f"Final Attachment URL after wait: {attachment.url}")
                encoded_url = urllib.parse.quote(attachment.url, safe='')
                page_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/image?full_url={encoded_url}"
                logging.info(f"Generated Page URL: {page_url}")
                await message.channel.send(f"이런 것도 혼자 못 하시나요...: {page_url}")


# Discord 봇 실행
def run_discord_bot():
    try:
        TOKEN = os.getenv("DISCORD_TOKEN")
        if not TOKEN:
            raise ValueError("ERROR: DISCORD_TOKEN environment variable is not set or empty.")
        logging.info(f"DISCORD_TOKEN successfully retrieved: {TOKEN[:10]}...")  # 토큰 일부만 출력 (보안)
        client.run(TOKEN)
    except Exception as e:
        logging.error(f"Error while running Discord bot: {e}")

if __name__ == "__main__":
    # Railway 환경 변수를 사용하여 포트 설정
    port = int(os.getenv("PORT", 8080))  # 기본값 8080
    threading.Thread(target=run_discord_bot, daemon=True).start()
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=port)

logging.info(f"Generated HTML: {html_template}")
