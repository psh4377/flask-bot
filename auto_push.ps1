# Git 자동 푸쉬 스크립트
# 스크립트를 저장하고 실행하세요.

# 작업 디렉토리 설정
$WorkingDirectory = "\\172.30.1.27\DiscordBot"  # Git 리포지토리 경로를 입력하세요.
Set-Location $WorkingDirectory

# 파일 변경 감지 및 푸쉬 함수
function Push-GitChanges {
    Write-Host "Git 자동 푸쉬 시작..." -ForegroundColor Green

    # git 상태 확인
    git status

    # 변경 사항 추가
    git add .

    # 현재 시간 기반으로 커밋 메시지 작성
    $CommitMessage = "Auto-commit: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"

    # 커밋
    git commit -m $CommitMessage

    # 푸쉬
    git push origin main

    Write-Host "변경 사항이 성공적으로 푸쉬되었습니다." -ForegroundColor Green
}

# Git 자동 푸쉬 실행
Push-GitChanges
