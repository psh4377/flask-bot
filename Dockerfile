# Python과 Node.js를 함께 사용하는 다중 단계 빌드 Dockerfile 예제

# Node.js 환경 추가
FROM node:18 as node-builder
WORKDIR /app
COPY package*.json ./
RUN npm install

# Python 환경 추가
FROM python:3.13-slim
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node.js 파일 복사
COPY --from=node-builder /app/node_modules ./node_modules
COPY --from=node-builder /app/package.json .

# Python 파일 복사
COPY . .

# Node.js와 Python 프로젝트 실행
CMD ["bash", "-c", "python bot.py & node index.js"]
