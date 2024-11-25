# Python 베이스 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사
COPY requirements.txt /app/

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . /app

# 봇 실행
CMD ["python", "bot.py"]
