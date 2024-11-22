# 베이스 이미지
FROM python:3.13-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

# 작업 디렉토리 설정
WORKDIR /app

# 요구사항 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 실행 명령어
CMD ["python", "bot.py"]
