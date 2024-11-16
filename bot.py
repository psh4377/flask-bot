import os
import discord
from flask import Flask, render_template_string, request
import urllib.parse
import asyncio
import threading

# Flask 앱 설정
app = Flask(__name__)

@app.route('/image')
def image_page():
    encoded_image_url = request.args.get('full_url', '').strip()
    full_image_url = urllib.parse.unquote(encoded_image_url)
    print(f"Full image URL received: {full_image_url}")

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
    return html_template

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                print(f"Initial Attachment URL: {attachment.url}")
                await asyncio.sleep(5)
                print(f"Final Attachment URL after wait: {attachment.url}")
                encoded_url = urllib.parse.quote(attachment.url, safe='')
                page_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/image?full_url={encoded_url}"
                print(f"Generated Page URL: {page_url}")
                await message.channel.send(f"Here's your preview link: {page_url}")

# Discord 봇 실행
def run_discord_bot():
    try:
        TOKEN = os.getenv("DISCORD_TOKEN")
        if not TOKEN:
            raise ValueError("ERROR: DISCORD_TOKEN environment variable is not set or empty.")
        print(f"DISCORD_TOKEN successfully retrieved: {TOKEN[:10]}...")  # 토큰 일부만 출력 (보안)
        client.run(TOKEN)
    except Exception as e:
        print(f"Error while running Discord bot: {e}")

if __name__ == "__main__":
    # 디스코드 봇 비동기 실행
    threading.Thread(target=run_discord_bot, daemon=True).start()
    # Flask 서버 실행
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=8080)
