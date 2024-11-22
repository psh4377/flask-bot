# 베이스 이미지 설정
FROM node:16 AS node-bot-stage

# Node.js 봇 설정
WORKDIR /node-bot

# Node.js 디펜던시 설치
COPY node-bot/package*.json ./
RUN npm install
COPY node-bot .

# Python 봇 설정
FROM python:3.13-slim AS python-bot-stage

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

WORKDIR /app

# Python 디펜던시 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 최종 단계: 둘 다 실행
FROM python:3.13-slim

# Node.js 봇 복사
COPY --from=node-bot-stage /node-bot /node-bot

# Python 봇 복사
COPY --from=python-bot-stage /app /app

# 실행 명령
WORKDIR /app
CMD ["sh", "-c", "node /node-bot/index.js & python bot.py"]
