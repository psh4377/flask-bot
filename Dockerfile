# Python 3.13 slim 이미지를 기반으로 컨테이너 생성
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 컨테이너 실행 명령어
CMD ["python", "bot.py"]
