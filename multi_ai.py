from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

multi_ai_bp = Blueprint('multi_ai', __name__)

@multi_ai_bp.route('/status', methods=['GET'])
def get_ai_status():
    """AI 상태 조회"""
    try:
        # 실제로는 각 AI 환경의 상태를 확인해야 함
        ai_status = {
            'manus': {
                'status': 'active',
                'last_activity': '2025-01-13T12:45:00Z',
                'capabilities': ['web_search', 'code_execution', 'file_system', 'image_generation'],
                'load': 0.3
            },
            'aiin': {
                'status': 'active', 
                'last_activity': '2025-01-13T12:44:30Z',
                'capabilities': ['gabriel_executor', 'system_commands', 'natural_language_processing'],
                'load': 0.2
            }
        }
        
        return jsonify({
            'success': True,
            'ai_environments': ai_status,
            'total_ais': len(ai_status)
        })
        
    except Exception as e:
        logger.error(f"AI 상태 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@multi_ai_bp.route('/capabilities', methods=['GET'])
def get_ai_capabilities():
    """AI 능력 조회"""
    try:
        capabilities = {
            'manus': {
                'name': 'Manus AI',
                'description': '범용 AI 에이전트로 다양한 도구를 활용한 종합적 작업 수행',
                'tools': [
                    {'name': 'web_search', 'description': '웹 검색 및 정보 수집'},
                    {'name': 'code_execution', 'description': '코드 작성 및 실행'},
                    {'name': 'file_system', 'description': '파일 시스템 조작'},
                    {'name': 'image_generation', 'description': '이미지 생성 및 편집'},
                    {'name': 'browser_automation', 'description': '웹 브라우저 자동화'},
                    {'name': 'data_analysis', 'description': '데이터 분석 및 시각화'}
                ],
                'strengths': ['종합적 분석', '다도구 활용', '복잡한 문제 해결'],
                'execution_environment': 'sandbox'
            },
            'aiin': {
                'name': 'AIIN',
                'description': 'Gabriel 실행기를 통한 직접적 시스템 명령 실행 전문 AI',
                'tools': [
                    {'name': 'gabriel_executor', 'description': 'Gabriel 명령 실행기'},
                    {'name': 'system_commands', 'description': '시스템 레벨 명령 실행'},
                    {'name': 'natural_language_processing', 'description': '자연어 명령 해석'},
                    {'name': 'command_validation', 'description': '명령어 안전성 검증'}
                ],
                'strengths': ['빠른 실행', '시스템 접근', '명령어 전문성'],
                'execution_environment': 'local'
            }
        }
        
        return jsonify({
            'success': True,
            'capabilities': capabilities
        })
        
    except Exception as e:
        logger.error(f"AI 능력 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@multi_ai_bp.route('/test-connection', methods=['POST'])
def test_ai_connection():
    """AI 연결 테스트"""
    try:
        data = request.get_json()
        ai_name = data.get('ai_name', 'all')
        
        test_results = {}
        
        if ai_name == 'all' or ai_name == 'manus':
            # Manus AI 연결 테스트 (시뮬레이션)
            test_results['manus'] = {
                'connected': True,
                'response_time': 150,  # ms
                'last_test': '2025-01-13T12:45:00Z',
                'status': 'healthy'
            }
        
        if ai_name == 'all' or ai_name == 'aiin':
            # AIIN 연결 테스트 (시뮬레이션)
            test_results['aiin'] = {
                'connected': True,
                'response_time': 80,  # ms
                'last_test': '2025-01-13T12:45:00Z',
                'status': 'healthy'
            }
        
        return jsonify({
            'success': True,
            'test_results': test_results
        })
        
    except Exception as e:
        logger.error(f"AI 연결 테스트 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@multi_ai_bp.route('/discussion-history', methods=['GET'])
def get_discussion_history():
    """토론 기록 조회"""
    try:
        # 실제로는 데이터베이스에서 조회해야 함
        history = [
            {
                'id': 1,
                'timestamp': '2025-01-13T12:30:00Z',
                'user_message': '파이썬으로 웹 크롤러를 만들어줘',
                'participants': ['manus', 'aiin'],
                'consensus': 'Manus가 코드 작성, AIIN이 실행 환경 준비',
                'result': '성공',
                'duration': 180  # seconds
            },
            {
                'id': 2,
                'timestamp': '2025-01-13T12:25:00Z',
                'user_message': '시스템 상태를 확인해줘',
                'participants': ['manus', 'aiin'],
                'consensus': 'AIIN이 시스템 명령 실행, Manus가 결과 분석',
                'result': '성공',
                'duration': 45
            }
        ]
        
        return jsonify({
            'success': True,
            'history': history,
            'total_discussions': len(history)
        })
        
    except Exception as e:
        logger.error(f"토론 기록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

