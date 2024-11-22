# Node.js 봇 빌드
FROM node:16 AS node-bot-stage

# 작업 디렉토리 설정
WORKDIR /node-bot

# Node.js 의존성 설치
COPY node-bot/package*.json ./  # package.json 및 package-lock.json 복사
RUN npm install
COPY node-bot ./  # Node.js 봇 파일 전체 복사

# Python 봇 빌드
FROM python:3.11-slim AS python-bot-stage

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt ./  # requirements.txt 복사
RUN pip install --no-cache-dir -r requirements.txt

# Python 소스 파일 복사
COPY bot.py /app/bot.py  # bot.py를 /app 디렉토리에 복사

# 최종 통합 이미지
FROM python:3.11-slim

# Node.js 봇 복사
COPY --from=node-bot-stage /node-bot /node-bot

# Python 봇 복사
COPY --from=python-bot-stage /app /app

# 작업 디렉토리 설정
WORKDIR /app

# Node.js와 Python 봇 병렬 실행
CMD ["sh", "-c", "ls /app && python -m pip list && python bot.py"]