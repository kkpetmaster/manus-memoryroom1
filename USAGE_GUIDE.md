# Manus 대화 백업 시스템 - 완전 사용법 가이드

## 🎯 목적
Manus 무료 크레딧 소진 시 새로운 계정으로 대화를 이어갈 수 있도록 실시간 백업 및 복원 시스템을 제공합니다.

## 📦 시스템 구성

### 1. 핵심 컴포넌트
- **백업 클라이언트** (`backup_client.py`): 대화 내용을 GitHub/GCS에 백업
- **Flask 웹 서비스** (`conversation_backup_service/`): 웹 인터페이스 및 API 제공
- **자동화 스크립트**: 백업/복원 자동화
- **상세 가이드**: 계정 간 이전 매뉴얼

### 2. 백업 저장소
- **GitHub Repository**: Private 저장소에 JSON 형태로 백업
- **Google Cloud Storage**: GCS 버킷에 실시간 백업 (선택사항)

## 🚀 빠른 시작 가이드

### 1단계: GitHub 설정
```bash
# 1. GitHub에서 새 Private Repository 생성
#    이름: manus-conversation-backup

# 2. Personal Access Token 생성
#    Settings > Developer settings > Personal access tokens
#    권한: repo (전체 저장소 접근)
```

### 2단계: 백업 서비스 실행
```bash
# 서비스 파일 압축 해제
unzip manus_backup_core.zip

# Flask 서비스 실행
cd conversation_backup_service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### 3단계: 웹 인터페이스 접속
1. 브라우저에서 `http://localhost:5000` 접속
2. 백업 설정 입력:
   - **사용자 ID**: 고유한 식별자 (예: `your_name_2025`)
   - **GitHub Token**: 생성한 Personal Access Token
   - **GitHub Repository**: `username/manus-conversation-backup`
3. "백업 시스템 초기화" 클릭

### 4단계: 대화 백업 시작
- 메시지 추가 시 자동으로 백업됩니다
- 수동 백업도 가능합니다
- 백업 상태를 실시간으로 확인할 수 있습니다

## 🔄 계정 간 이전 프로세스

### 현재 계정에서 (크레딧 소진 전)
1. 백업 시스템 초기화 및 활성화
2. 모든 대화 내용 백업 확인
3. 대화 ID 기록 (예: `conv_1720851234_abc123def`)
4. 설정 정보 저장 (GitHub Token, Repository 등)

### 새 계정에서 (이전 후)
1. 새 Manus 계정 생성
2. 동일한 백업 서비스 실행
3. **동일한 설정**으로 초기화:
   - 사용자 ID: 이전과 동일
   - GitHub Token: 동일
   - Repository: 동일
4. "대화 복원" 섹션에서 대화 ID 입력
5. "대화 복원" 실행

## 🛠️ API 사용법

### 백업 시스템 초기화
```python
import requests

url = "http://localhost:5000/api/backup/init"
data = {
    "user_id": "your_unique_id",
    "github_token": "your_github_token",
    "github_repo": "username/repository-name",
    "backup_interval": 30
}

response = requests.post(url, json=data)
print(response.json())
```

### 메시지 추가
```python
url = "http://localhost:5000/api/backup/message"
data = {
    "user_id": "your_unique_id",
    "role": "user",
    "content": "안녕하세요!",
    "attachments": [],
    "function_calls": []
}

response = requests.post(url, json=data)
print(response.json())
```

### 대화 복원
```python
conversation_id = "conv_1720851234_abc123def"
url = f"http://localhost:5000/api/backup/restore/{conversation_id}"
params = {
    "user_id": "your_unique_id",
    "source": "github"
}

response = requests.get(url, params=params)
restored_data = response.json()
```

## 🔧 자동화 스크립트

### 백업 자동화
```python
# 파일: auto_backup.py
from backup_client import ConversationBackupClient

config = {
    'github_token': 'your_token',
    'github_repo': 'username/repo',
    'user_id': 'your_id'
}

client = ConversationBackupClient(config)
client.add_message("user", "메시지 내용")
```

### 복원 자동화
```python
# 파일: auto_restore.py
import requests

def restore_conversation(conversation_id):
    # 백업 시스템 초기화
    init_response = requests.post("http://localhost:5000/api/backup/init", json={
        "user_id": "your_id",
        "github_token": "your_token",
        "github_repo": "username/repo"
    })
    
    # 대화 복원
    restore_response = requests.get(
        f"http://localhost:5000/api/backup/restore/{conversation_id}",
        params={"user_id": "your_id", "source": "github"}
    )
    
    return restore_response.json()
```

## 📋 체크리스트

### 백업 준비 체크리스트
- [ ] GitHub Private Repository 생성
- [ ] Personal Access Token 생성 (repo 권한)
- [ ] 백업 서비스 실행 및 테스트
- [ ] 초기 설정 완료 및 확인
- [ ] 첫 번째 메시지 백업 테스트
- [ ] 백업 상태 확인

### 계정 이전 체크리스트
- [ ] 새 Manus 계정 생성
- [ ] 백업 서비스 재실행
- [ ] 동일한 설정으로 초기화
- [ ] 대화 목록 조회 확인
- [ ] 대화 복원 실행
- [ ] 복원된 내용 검증
- [ ] 새 계정에서 작업 재개

## ⚠️ 주의사항

### 보안
- GitHub Token은 안전하게 보관하세요
- Private Repository만 사용하세요
- 민감한 정보는 별도로 관리하세요

### 제한사항
- GitHub API 호출 제한 (시간당 5,000회)
- 대용량 파일은 별도 처리 필요
- 네트워크 연결 필수

### 백업 주기
- 기본 30초 간격으로 자동 백업
- 중요한 시점에서 수동 백업 권장
- 정기적인 백업 상태 확인

## 🆘 문제 해결

### 백업 실패
1. GitHub Token 권한 확인
2. Repository 접근 권한 확인
3. 네트워크 연결 상태 확인
4. API 호출 제한 확인

### 복원 실패
1. 대화 ID 정확성 확인
2. 백업 파일 존재 여부 확인
3. 설정 정보 일치 여부 확인
4. GitHub Repository 접근 권한 확인

### 연속성 문제
1. 컨텍스트 정보 수동 확인
2. 파일 경로 및 상태 확인
3. 작업 단계 재확인
4. 백업 데이터 무결성 검증

## 📞 지원

이 시스템을 통해 Manus 계정 간 완벽한 대화 연속성을 보장할 수 있습니다. 
문제가 발생하면 백업된 데이터를 확인하고 위의 문제 해결 가이드를 참조하세요.

**백업 서비스 URL**: https://5000-i3vz48pw09a92bu8aujdm-3154416d.manusvm.computer

---
*이 시스템은 Manus 사용자의 편의를 위해 개발되었습니다. 안전한 사용을 위해 가이드를 숙지하고 사용하세요.*

