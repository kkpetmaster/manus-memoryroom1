from flask import Blueprint, request, jsonify
import subprocess
import os
import threading
import time
from typing import Dict, Any
import logging

terminal_bp = Blueprint('terminal', __name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerminalSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.working_dir = "/home/ubuntu"
        self.env = os.environ.copy()
        self.history = []
        self.last_activity = time.time()
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        명령어 실행
        """
        try:
            self.last_activity = time.time()
            
            # 보안을 위한 명령어 필터링
            if self._is_dangerous_command(command):
                return {
                    "output": "보안상 실행할 수 없는 명령어입니다.",
                    "error": "Command blocked for security reasons",
                    "exit_code": 1,
                    "command": command
                }
            
            # cd 명령어 특별 처리
            if command.strip().startswith('cd '):
                return self._handle_cd_command(command)
            
            # 명령어 실행
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                env=self.env,
                capture_output=True,
                text=True,
                timeout=30  # 30초 타임아웃
            )
            
            output = result.stdout
            error = result.stderr
            exit_code = result.returncode
            
            # 히스토리에 추가
            self.history.append({
                "command": command,
                "output": output,
                "error": error,
                "exit_code": exit_code,
                "timestamp": time.time(),
                "working_dir": self.working_dir
            })
            
            return {
                "output": output,
                "error": error,
                "exit_code": exit_code,
                "command": command,
                "working_dir": self.working_dir
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": "명령어 실행 시간이 초과되었습니다 (30초).",
                "exit_code": 124,
                "command": command
            }
        except Exception as e:
            logger.error(f"명령어 실행 오류: {str(e)}")
            return {
                "output": "",
                "error": f"명령어 실행 중 오류가 발생했습니다: {str(e)}",
                "exit_code": 1,
                "command": command
            }
    
    def _is_dangerous_command(self, command: str) -> bool:
        """
        위험한 명령어인지 확인
        """
        dangerous_commands = [
            'rm -rf /',
            'sudo rm',
            'mkfs',
            'dd if=',
            'shutdown',
            'reboot',
            'halt',
            'init 0',
            'init 6',
            'killall',
            'pkill -9',
            'chmod 777 /',
            'chown -R',
            '> /dev/sda',
            'format',
            'fdisk'
        ]
        
        command_lower = command.lower().strip()
        return any(dangerous in command_lower for dangerous in dangerous_commands)
    
    def _handle_cd_command(self, command: str) -> Dict[str, Any]:
        """
        cd 명령어 처리
        """
        try:
            # cd 명령어에서 경로 추출
            parts = command.strip().split(' ', 1)
            if len(parts) == 1:
                # cd만 입력된 경우 홈 디렉토리로
                new_dir = "/home/ubuntu"
            else:
                path = parts[1].strip()
                if path.startswith('/'):
                    # 절대 경로
                    new_dir = path
                else:
                    # 상대 경로
                    new_dir = os.path.join(self.working_dir, path)
            
            # 경로 정규화
            new_dir = os.path.abspath(new_dir)
            
            # 경로 존재 확인
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                self.working_dir = new_dir
                return {
                    "output": f"디렉토리가 변경되었습니다: {new_dir}",
                    "error": "",
                    "exit_code": 0,
                    "command": command,
                    "working_dir": self.working_dir
                }
            else:
                return {
                    "output": "",
                    "error": f"디렉토리를 찾을 수 없습니다: {new_dir}",
                    "exit_code": 1,
                    "command": command,
                    "working_dir": self.working_dir
                }
                
        except Exception as e:
            return {
                "output": "",
                "error": f"cd 명령어 처리 중 오류: {str(e)}",
                "exit_code": 1,
                "command": command,
                "working_dir": self.working_dir
            }
    
    def get_history(self, limit: int = 50) -> list:
        """
        명령어 히스토리 반환
        """
        return self.history[-limit:] if limit > 0 else self.history

# 터미널 세션 관리
terminal_sessions: Dict[str, TerminalSession] = {}

def cleanup_old_sessions():
    """
    오래된 세션 정리 (1시간 이상 비활성)
    """
    current_time = time.time()
    sessions_to_remove = []
    
    for session_id, session in terminal_sessions.items():
        if current_time - session.last_activity > 3600:  # 1시간
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del terminal_sessions[session_id]
        logger.info(f"터미널 세션 정리: {session_id}")

@terminal_bp.route('/execute', methods=['POST'])
def execute_command():
    """
    터미널 명령어 실행
    """
    try:
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({
                "error": "명령어가 필요합니다.",
                "status": "error"
            }), 400
        
        command = data['command']
        session_id = data.get('session_id', 'default')
        
        # 세션 가져오기 또는 생성
        if session_id not in terminal_sessions:
            terminal_sessions[session_id] = TerminalSession(session_id)
        
        session = terminal_sessions[session_id]
        
        # 명령어 실행
        result = session.execute_command(command)
        
        # 오래된 세션 정리
        cleanup_old_sessions()
        
        return jsonify({
            "result": result,
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"터미널 명령어 실행 오류: {str(e)}")
        return jsonify({
            "error": f"서버 오류가 발생했습니다: {str(e)}",
            "status": "error"
        }), 500

@terminal_bp.route('/history', methods=['GET'])
def get_history():
    """
    터미널 히스토리 조회
    """
    try:
        session_id = request.args.get('session_id', 'default')
        limit = int(request.args.get('limit', 50))
        
        if session_id not in terminal_sessions:
            return jsonify({
                "history": [],
                "session_id": session_id,
                "status": "success"
            })
        
        session = terminal_sessions[session_id]
        history = session.get_history(limit)
        
        return jsonify({
            "history": history,
            "session_id": session_id,
            "working_dir": session.working_dir,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"터미널 히스토리 조회 오류: {str(e)}")
        return jsonify({
            "error": f"서버 오류가 발생했습니다: {str(e)}",
            "status": "error"
        }), 500

@terminal_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    활성 터미널 세션 목록 조회
    """
    try:
        sessions_info = []
        for session_id, session in terminal_sessions.items():
            sessions_info.append({
                "session_id": session_id,
                "working_dir": session.working_dir,
                "last_activity": session.last_activity,
                "command_count": len(session.history)
            })
        
        return jsonify({
            "sessions": sessions_info,
            "total": len(sessions_info),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"터미널 세션 조회 오류: {str(e)}")
        return jsonify({
            "error": f"서버 오류가 발생했습니다: {str(e)}",
            "status": "error"
        }), 500

@terminal_bp.route('/clear', methods=['POST'])
def clear_session():
    """
    터미널 세션 초기화
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default') if data else 'default'
        
        if session_id in terminal_sessions:
            terminal_sessions[session_id].history = []
            terminal_sessions[session_id].working_dir = "/home/ubuntu"
        
        return jsonify({
            "message": "터미널 세션이 초기화되었습니다.",
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"터미널 세션 초기화 오류: {str(e)}")
        return jsonify({
            "error": f"서버 오류가 발생했습니다: {str(e)}",
            "status": "error"
        }), 500

