# Node.js 환경 설정
FROM node:18 as node-builder
WORKDIR /app

# Node.js 패키지 설치
COPY package*.json ./
RUN npm install

# Python 환경 설정
FROM python:3.13-slim
WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node.js 및 Python 소스 복사
COPY . .

# 실행 명령
CMD ["bash", "-c", "python bot.py & node index.js"]
