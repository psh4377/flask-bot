# Node.js 봇 빌드
FROM node:16 AS node-bot-stage

# 작업 디렉토리 설정
WORKDIR /node-bot

# Node.js 의존성 설치
COPY node-bot/package*.json ./
RUN npm install
COPY node-bot ./

# Python 봇 빌드
FROM python:3.11-slim
 AS python-bot-stage

# Dockerfile의 RUN 명령에 --no-cache 옵션 추가
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

WORKDIR /app

# Python 의존성 설치
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir discord.py==2.4.0

COPY . ./

# 최종 통합 이미지
FROM python:3.11-slim

CMD ["sh", "-c", "echo 'Starting bot.py...' && python bot.py"]

# Node.js 봇 복사
COPY --from=node-bot-stage /node-bot /node-bot

# Python 봇 복사
COPY --from=python-bot-stage /app /app

# 작업 디렉토리 설정
WORKDIR /app

# Node.js와 Python 봇 병렬 실행
CMD ["sh", "-c", "node /node-bot/index.js & python bot.py"]
