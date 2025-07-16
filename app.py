from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import re
import os
import logging

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 허용된 명령어 패턴
ALLOWED_COMMANDS = {
    'nginx': ['nginx -t', 'sudo systemctl restart nginx', 'sudo systemctl status nginx'],
    'docker': ['docker ps', 'docker images', 'docker-compose ps'],
    'system': ['whoami', 'uptime', 'date', 'pwd', 'ls -la'],
    'chatweb': ['npm run build', 'npm start', 'npm test']
}

def is_safe_command(command):
    """명령어가 안전한지 확인"""
    # 위험한 명령어 차단
    dangerous_patterns = [
        r'\brm\b.*-rf',
        r'\bsudo\s+rm\b',
        r'\breboot\b',
        r'\bshutdown\b',
        r'\bpasswd\b',
        r'\bsu\b',
        r'\bmkfs\b',
        r'\bdd\b.*if=',
        r'\bformat\b',
        r'\bdel\b.*\*',
        r'>\s*/dev/',
        r'\|.*sh\b',
        r';\s*rm\b',
        r'&&.*rm\b'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    return True

def parse_korean_command(command):
    """한글 명령어를 영어 명령어로 변환"""
    korean_mappings = {
        '재시작': 'restart',
        '상태': 'status',
        '확인': 'check',
        '빌드': 'build',
        '실행': 'run',
        '중지': 'stop',
        '시작': 'start',
        '목록': 'list',
        '정보': 'info'
    }
    
    # AIIN 명령어 패턴 처리
    if 'aiin' in command.lower():
        # "AIIN, nginx 재시작해줘" -> "nginx restart"
        command = re.sub(r'aiin,?\s*', '', command, flags=re.IGNORECASE)
        command = re.sub(r'해줘|하세요|해주세요', '', command)
        
        for korean, english in korean_mappings.items():
            command = command.replace(korean, english)
    
    return command.strip()

def execute_command(command):
    """명령어 실행"""
    try:
        # 한글 명령어 변환
        parsed_command = parse_korean_command(command)
        
        # 안전성 검사
        if not is_safe_command(parsed_command):
            return {
                'success': False,
                'output': '위험한 명령어는 실행할 수 없습니다.',
                'error': 'Dangerous command blocked'
            }
        
        # 명령어 실행
        logger.info(f"Executing command: {parsed_command}")
        
        result = subprocess.run(
            parsed_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': '명령어 실행 시간이 초과되었습니다.',
            'return_code': -1
        }
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'return_code': -1
        }

@app.route('/api/execute', methods=['POST'])
def execute():
    """명령어 실행 API"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({
                'success': False,
                'message': '명령어가 입력되지 않았습니다.'
            }), 400
        
        # 명령어 실행
        result = execute_command(command)
        
        # 응답 생성
        response = {
            'success': result['success'],
            'command': command,
            'output': result['output'],
            'error': result['error'],
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
        }
        
        if result['success']:
            response['message'] = f"명령어 '{command}' 실행 완료"
        else:
            response['message'] = f"명령어 '{command}' 실행 실패: {result['error']}"
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'서버 오류: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """서버 상태 확인"""
    return jsonify({
        'status': 'running',
        'message': 'AIIN Gabriel 실행기가 정상 작동 중입니다.',
        'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
    })

@app.route('/health', methods=['GET'])
def health():
    """헬스체크"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

