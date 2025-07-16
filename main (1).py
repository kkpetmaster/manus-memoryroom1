import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
from src.models.user import db
from src.routes.user import user_bp
from src.routes.multi_ai import multi_ai_bp
from src.ai_environments import ManusEnvironment, AIINEnvironment

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'multi-ai-chatweb-secret-key-2025'

# CORS 설정
CORS(app, origins="*")

# SocketIO 설정
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Blueprint 등록
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(multi_ai_bp, url_prefix='/api/ai')

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# 다중 AI 오케스트레이터
class MultiAIOrchestrator:
    def __init__(self):
        self.ai_environments = {
            'manus': ManusEnvironment(),
            'aiin': AIINEnvironment()
        }
        self.active_sessions = {}
        self.discussion_states = {}
    
    async def handle_user_message(self, session_id: str, message: str):
        """사용자 메시지 처리 및 AI 토론 시작"""
        try:
            logger.info(f"Session {session_id}: 사용자 메시지 처리 시작 - {message}")
            
            # 1. 초기 분석 단계
            socketio.emit('discussion_update', {
                'discussion_state': 'analyzing',
                'discussion_content': '각 AI가 요청을 분석하고 있습니다...'
            }, room=session_id)
            
            # 2. 각 AI에게 메시지 전달 및 초기 응답 수집
            ai_responses = await self.collect_initial_responses(session_id, message)
            
            # 3. 토론 프로세스 시작
            socketio.emit('discussion_update', {
                'discussion_state': 'discussing',
                'discussion_content': 'AI들이 서로의 의견을 검토하고 토론하고 있습니다...'
            }, room=session_id)
            
            discussion_result = await self.facilitate_discussion(session_id, ai_responses)
            
            # 4. 합의 도출
            socketio.emit('discussion_update', {
                'discussion_state': 'consensus'
            }, room=session_id)
            
            consensus = await self.reach_consensus(session_id, discussion_result)
            
            # 5. 합의된 계획 실행
            socketio.emit('discussion_update', {
                'discussion_state': 'executing'
            }, room=session_id)
            
            execution_result = await self.execute_consensus_plan(session_id, consensus)
            
            # 6. 최종 결과 전달
            socketio.emit('execution_result', {
                'result': execution_result
            }, room=session_id)
            
        except Exception as e:
            logger.error(f"Session {session_id}: 오류 발생 - {str(e)}")
            socketio.emit('error', {
                'message': f'처리 중 오류가 발생했습니다: {str(e)}'
            }, room=session_id)
    
    async def collect_initial_responses(self, session_id: str, message: str) -> Dict[str, Any]:
        """각 AI로부터 초기 응답 수집"""
        responses = {}
        
        for ai_name, ai_env in self.ai_environments.items():
            try:
                logger.info(f"Session {session_id}: {ai_name} AI 응답 요청")
                response = await ai_env.analyze_request(message)
                responses[ai_name] = response
                
                # 각 AI의 응답을 실시간으로 전송
                socketio.emit('ai_response', {
                    'ai_name': ai_name,
                    'content': f"[초기 분석] {response.get('analysis', '분석 중...')}"
                }, room=session_id)
                
            except Exception as e:
                logger.error(f"Session {session_id}: {ai_name} AI 응답 오류 - {str(e)}")
                responses[ai_name] = {'error': str(e)}
        
        return responses
    
    async def facilitate_discussion(self, session_id: str, ai_responses: Dict[str, Any]) -> Dict[str, Any]:
        """AI 간 토론 진행"""
        discussion_rounds = []
        
        # 각 AI가 다른 AI의 의견을 검토하고 피드백 제공
        for round_num in range(2):  # 2라운드 토론
            round_feedback = {}
            
            for ai_name, ai_env in self.ai_environments.items():
                if ai_name in ai_responses and 'error' not in ai_responses[ai_name]:
                    try:
                        # 다른 AI들의 의견을 검토
                        other_responses = {k: v for k, v in ai_responses.items() if k != ai_name}
                        feedback = await ai_env.review_and_feedback(other_responses, round_num)
                        round_feedback[ai_name] = feedback
                        
                        # 토론 내용을 실시간으로 전송
                        socketio.emit('ai_response', {
                            'ai_name': ai_name,
                            'content': f"[토론 {round_num + 1}라운드] {feedback.get('feedback', '검토 중...')}"
                        }, room=session_id)
                        
                    except Exception as e:
                        logger.error(f"Session {session_id}: {ai_name} 토론 오류 - {str(e)}")
            
            discussion_rounds.append(round_feedback)
        
        return {
            'initial_responses': ai_responses,
            'discussion_rounds': discussion_rounds
        }
    
    async def reach_consensus(self, session_id: str, discussion_result: Dict[str, Any]) -> Dict[str, Any]:
        """합의 도출"""
        try:
            # 각 AI의 최종 제안을 종합
            final_proposals = {}
            
            for ai_name, ai_env in self.ai_environments.items():
                try:
                    proposal = await ai_env.generate_final_proposal(discussion_result)
                    final_proposals[ai_name] = proposal
                except Exception as e:
                    logger.error(f"Session {session_id}: {ai_name} 최종 제안 오류 - {str(e)}")
            
            # 합의 알고리즘: 협업 점수가 높은 제안 선택
            best_proposal = None
            best_score = 0
            
            for ai_name, proposal in final_proposals.items():
                if 'error' not in proposal:
                    confidence = proposal.get('confidence', 0.5)
                    if confidence > best_score:
                        best_score = confidence
                        best_proposal = proposal
            
            if best_proposal is None:
                best_proposal = {'action': 'error', 'message': '합의에 실패했습니다.'}
            
            # 합의 결과 전송
            socketio.emit('consensus_reached', {
                'consensus': f"합의된 계획: {best_proposal.get('summary', '계획을 실행합니다.')}"
            }, room=session_id)
            
            return best_proposal
            
        except Exception as e:
            logger.error(f"Session {session_id}: 합의 도출 오류 - {str(e)}")
            return {'action': 'error', 'message': str(e)}
    
    async def execute_consensus_plan(self, session_id: str, consensus: Dict[str, Any]) -> str:
        """합의된 계획 실행"""
        try:
            if consensus.get('action') == 'error':
                return consensus.get('message', '실행할 수 없습니다.')
            
            # 실행 담당 AI 결정
            executor = consensus.get('executor', 'manus')
            
            if executor == 'both':
                # 협업 실행
                results = []
                workflow = consensus.get('workflow', [])
                
                for step in workflow:
                    actor = step.get('actor')
                    if actor in self.ai_environments:
                        step_result = await self.ai_environments[actor]._execute_aiin_step(step) if actor == 'aiin' else await self.ai_environments[actor]._execute_manus_step(step)
                        results.append(f"[{actor.upper()}] {step_result}")
                
                return "협업 실행 완료:\n" + "\n".join(results)
            
            elif executor in self.ai_environments:
                result = await self.ai_environments[executor].execute_plan(consensus)
                return result
            else:
                return "실행할 AI를 찾을 수 없습니다."
                
        except Exception as e:
            logger.error(f"Session {session_id}: 계획 실행 오류 - {str(e)}")
            return f"실행 중 오류가 발생했습니다: {str(e)}"

# 전역 오케스트레이터 인스턴스
orchestrator = MultiAIOrchestrator()

# SocketIO 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    logger.info(f"클라이언트 연결: {request.sid}")
    emit('connected', {'message': '다중 AI 채팅에 연결되었습니다.'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"클라이언트 연결 해제: {request.sid}")

@socketio.on('user_message')
def handle_user_message(data):
    """사용자 메시지 처리"""
    session_id = request.sid
    message = data.get('content', '')
    
    logger.info(f"Session {session_id}: 사용자 메시지 수신 - {message}")
    
    # 비동기 처리를 위해 새 스레드에서 실행
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(orchestrator.handle_user_message(session_id, message))
        loop.close()
    
    import threading
    thread = threading.Thread(target=run_async)
    thread.start()

# HTTP 라우트
@app.route('/api/health')
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_environments': list(orchestrator.ai_environments.keys())
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("다중 AI 채팅 웹 서버 시작")
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)

