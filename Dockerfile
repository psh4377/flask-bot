# Node.js 설치를 위한 기본 이미지
FROM node:18 AS node-builder
WORKDIR /app

# Node.js 종속성 설치
COPY package*.json ./
RUN npm install

# Python 환경 설정
FROM python:3.13-slim
WORKDIR /app

# Python 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node.js 빌드 결과 및 Python 소스 복사
COPY --from=node-builder /app /app

# 시작 명령어 설정
CMD ["sh", "-c", "node index.js & python bot.py"]
