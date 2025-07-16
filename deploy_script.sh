#!/bin/bash

# Chavion AI Platform 배포 스크립트
# VM에서 실행할 스크립트입니다.

echo "=== Chavion AI Platform 배포 시작 ==="

# 1. 시스템 업데이트
echo "시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 2. 필요한 패키지 설치
echo "필요한 패키지 설치 중..."
sudo apt install -y curl git nodejs npm python3 python3-pip nginx

# 3. GitHub 저장소 클론
echo "GitHub 저장소 클론 중..."
cd /home/ubuntu
git clone https://github.com/kkpetmaster/manus-memoryroom.git
cd manus-memoryroom

# 4. Python 의존성 설치
echo "Python 의존성 설치 중..."
pip3 install flask flask-cors requests

# 5. Node.js 의존성 설치
echo "Node.js 의존성 설치 중..."
npm install

# 6. React 프로젝트 빌드
echo "React 프로젝트 빌드 중..."
npm run build

# 7. Nginx 설정
echo "Nginx 설정 중..."
sudo tee /etc/nginx/sites-available/chavion > /dev/null <<EOF
server {
    listen 80;
    server_name chavion.com www.chavion.com;
    
    # React 정적 파일 서빙
    location / {
        root /home/ubuntu/manus-memoryroom/build;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Flask API 프록시
    location /api/ {
        proxy_pass http://localhost:4000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 8. Nginx 사이트 활성화
sudo ln -sf /etc/nginx/sites-available/chavion /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 9. Nginx 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# 10. Flask 서비스 설정
echo "Flask 서비스 설정 중..."
sudo tee /etc/systemd/system/chavion-api.service > /dev/null <<EOF
[Unit]
Description=Chavion AI Platform API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/manus-memoryroom
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 11. Flask 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable chavion-api
sudo systemctl start chavion-api

# 12. 방화벽 설정
echo "방화벽 설정 중..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

echo "=== 배포 완료! ==="
echo "Chavion AI Platform이 http://chavion.com 에서 접속 가능합니다."
echo ""
echo "서비스 상태 확인:"
echo "- Nginx: sudo systemctl status nginx"
echo "- Flask API: sudo systemctl status chavion-api"
echo ""
echo "로그 확인:"
echo "- Nginx 로그: sudo tail -f /var/log/nginx/error.log"
echo "- Flask 로그: sudo journalctl -u chavion-api -f"

