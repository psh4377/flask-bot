FROM python:3.13-slim

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py", "/app/bot.py"]
RUN mkdir -p /tmp/audio && chmod -R 777 /tmp/audio
WORKDIR /tmp/audio
