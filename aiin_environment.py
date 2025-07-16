import asyncio
import logging
import subprocess
import re
import os
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AIINEnvironment:
    """AIIN AI 실행 환경 (Gabriel 실행기 포함)"""
    
    def __init__(self):
        self.gabriel_executor = GabrielExecutor()
        self.nlp_processor = AIINNLPProcessor()
        self.command_validator = CommandValidator()
        self.tools_available = [
            'gabriel_executor', 'system_commands', 
            'natural_language_processing', 'command_validation'
        ]
        self.current_context = {}
    
    async def analyze_request(self, message: str) -> Dict[str, Any]:
        """사용자 요청 분석"""
        try:
            logger.info(f"AIIN: 요청 분석 시작 - {message}")
            
            # 자연어 처리를 통한 명령어 분석
            await asyncio.sleep(1)  # 분석 시간 시뮬레이션
            
            analysis = await self._analyze_command_intent(message)
            
            logger.info(f"AIIN: 분석 완료 - {analysis['summary']}")
            return analysis
            
        except Exception as e:
            logger.error(f"AIIN 분석 오류: {str(e)}")
            return {
                'error': str(e),
                'analysis': '분석 중 오류가 발생했습니다.',
                'confidence': 0.0
            }
    
    async def _analyze_command_intent(self, message: str) -> Dict[str, Any]:
        """명령어 의도 분석"""
        # 자연어를 시스템 명령어로 변환하는 로직
        keywords = message.lower()
        
        if any(word in keywords for word in ['파일', 'file', '목록', 'list', 'ls']):
            return {
                'analysis': f'파일 시스템 조작 명령으로 해석됩니다: "{message}"',
                'approach': 'direct_execution',
                'command_type': 'file_system',
                'suggested_commands': ['ls -la', 'find', 'cat'],
                'confidence': 0.9,
                'summary': '파일 시스템 직접 실행',
                'safety_level': 'safe'
            }
        elif any(word in keywords for word in ['프로세스', 'process', '실행', 'run', 'ps']):
            return {
                'analysis': f'프로세스 관리 명령으로 해석됩니다: "{message}"',
                'approach': 'direct_execution',
                'command_type': 'process_management',
                'suggested_commands': ['ps aux', 'top', 'htop'],
                'confidence': 0.85,
                'summary': '프로세스 관리 직접 실행',
                'safety_level': 'safe'
            }
        elif any(word in keywords for word in ['시스템', 'system', '상태', 'status', '정보']):
            return {
                'analysis': f'시스템 정보 조회 명령으로 해석됩니다: "{message}"',
                'approach': 'direct_execution',
                'command_type': 'system_info',
                'suggested_commands': ['whoami', 'uptime', 'df -h', 'free -h'],
                'confidence': 0.95,
                'summary': '시스템 정보 직접 조회',
                'safety_level': 'safe'
            }
        elif any(word in keywords for word in ['네트워크', 'network', '연결', 'connection', 'ping']):
            return {
                'analysis': f'네트워크 관련 명령으로 해석됩니다: "{message}"',
                'approach': 'direct_execution',
                'command_type': 'network',
                'suggested_commands': ['ping', 'netstat', 'ss'],
                'confidence': 0.8,
                'summary': '네트워크 상태 직접 확인',
                'safety_level': 'safe'
            }
        else:
            return {
                'analysis': f'일반적인 시스템 명령으로 해석하여 Gabriel 실행기로 처리합니다: "{message}"',
                'approach': 'gabriel_execution',
                'command_type': 'general',
                'suggested_commands': ['echo', 'date', 'pwd'],
                'confidence': 0.7,
                'summary': 'Gabriel 실행기를 통한 일반 명령 처리',
                'safety_level': 'safe'
            }
    
    async def review_and_feedback(self, other_responses: Dict[str, Any], round_num: int) -> Dict[str, Any]:
        """다른 AI 응답 검토 및 피드백"""
        try:
            logger.info(f"AIIN: 토론 {round_num + 1}라운드 - 다른 AI 응답 검토")
            
            await asyncio.sleep(0.8)  # 검토 시간 시뮬레이션
            
            feedback = await self._generate_aiin_feedback(other_responses, round_num)
            
            logger.info(f"AIIN: 피드백 생성 완료")
            return feedback
            
        except Exception as e:
            logger.error(f"AIIN 피드백 생성 오류: {str(e)}")
            return {
                'error': str(e),
                'feedback': '피드백 생성 중 오류가 발생했습니다.',
                'round': round_num
            }
    
    async def _generate_aiin_feedback(self, other_responses: Dict[str, Any], round_num: int) -> Dict[str, Any]:
        """AIIN 피드백 생성 (개선된 로직)"""
        manus_response = other_responses.get("manus", {})

        if "error" in manus_response:
            return {
                "feedback": "Manus AI에서 오류가 발생했습니다. Gabriel 실행기를 통해 단독으로 작업을 수행하겠습니다.",
                "suggestions": ["solo_gabriel_execution", "error_recovery"],
                "collaboration_score": 0.2,
                "round": round_num
            }

        manus_approach = manus_response.get("approach", "unknown")
        manus_tools = manus_response.get("tools_needed", [])
        manus_plan = manus_response.get("plan", [])

        # Manus의 계획을 분석하여 더 구체적인 피드백 생성
        if manus_plan:
            feedback = f"Manus AI가 {len(manus_plan)}단계의 상세 계획을 제시했습니다. 계획의 각 단계에서 Gabriel 실행기를 활용하여 시스템 레벨 작업을 효율적으로 지원할 수 있습니다."
            suggestions = ["detailed_plan_collaboration", "step_by_step_execution_support"]
            collaboration_score = 0.95
            proposed_workflow = []
            for i, step in enumerate(manus_plan):
                # Manus의 계획 단계에 맞춰 AIIN의 역할을 제안
                if any(keyword in step.lower() for keyword in ["파일", "시스템", "설치", "실행", "명령"]):
                    proposed_workflow.append(f"{i+1}단계 ({step}): AIIN(Gabriel)이 시스템 명령 실행 지원")
                else:
                    proposed_workflow.append(f"{i+1}단계 ({step}): Manus가 주도적으로 작업 수행")
            
            return {
                "feedback": feedback,
                "suggestions": suggestions,
                "collaboration_score": collaboration_score,
                "round": round_num,
                "proposed_workflow": proposed_workflow
            }

        elif manus_approach == "comprehensive" and "code_execution" in manus_tools:
            return {
                "feedback": f"Manus AI의 종합적 접근법이 훌륭합니다. 제가 시스템 레벨에서 실제 명령 실행을 담당하고, Manus가 상위 레벨 로직을 담당하는 분업을 제안합니다.",
                "suggestions": ["system_level_execution", "manus_logic_aiin_execution"],
                "collaboration_score": 0.9,
                "round": round_num,
                "proposed_workflow": [
                    "Manus: 전체적인 계획 수립 및 로직 설계",
                    "AIIN: Gabriel을 통한 시스템 명령 실행",
                    "Manus: 결과 분석 및 다음 단계 결정",
                    "AIIN: 추가 명령 실행 (필요시)"
                ]
            }
        elif "web_search" in manus_tools:
            return {
                "feedback": f"Manus AI가 웹 검색을 담당하는 동안, 저는 로컬 시스템에서 필요한 환경 설정이나 파일 준비를 Gabriel로 수행하겠습니다.",
                "suggestions": ["parallel_execution", "manus_web_aiin_local"],
                "collaboration_score": 0.85,
                "round": round_num
            }
        else:
            return {
                "feedback": f"Manus AI의 접근법을 보완하여 Gabriel 실행기의 빠른 시스템 명령 실행 능력을 활용하겠습니다.",
                "suggestions": ["complementary_execution", "gabriel_acceleration"],
                "collaboration_score": 0.75,
                "round": round_num
            }

    async def generate_final_proposal(self, discussion_result: Dict[str, Any]) -> Dict[str, Any]:
        """최종 제안 생성"""
        try:
            logger.info("AIIN: 최종 제안 생성")
            
            await asyncio.sleep(0.8)
            
            # 토론 결과를 바탕으로 최종 제안 생성
            initial_responses = discussion_result.get('initial_responses', {})
            discussion_rounds = discussion_result.get('discussion_rounds', [])
            
            my_analysis = initial_responses.get('aiin', {})
            manus_analysis = initial_responses.get('manus', {})
            
            # 협업 점수 계산
            collaboration_scores = []
            for round_data in discussion_rounds:
                if 'aiin' in round_data:
                    score = round_data['aiin'].get('collaboration_score', 0.5)
                    collaboration_scores.append(score)
            
            avg_collaboration = sum(collaboration_scores) / len(collaboration_scores) if collaboration_scores else 0.5
            
            if avg_collaboration > 0.8:
                # 높은 협업 점수 - 협업 실행 제안
                proposal = {
                    'summary': 'Gabriel 실행기와 Manus AI의 협업을 통한 효율적 실행',
                    'action': 'collaborative_execute',
                    'executor': 'both',
                    'workflow': [
                        {'step': 1, 'actor': 'aiin', 'action': '시스템 환경 확인 및 준비'},
                        {'step': 2, 'actor': 'manus', 'action': '상세 계획 수립 및 리소스 분석'},
                        {'step': 3, 'actor': 'aiin', 'action': 'Gabriel을 통한 핵심 명령 실행'},
                        {'step': 4, 'actor': 'manus', 'action': '결과 검증 및 후속 작업'}
                    ],
                    'estimated_time': '1-3분',
                    'confidence': 0.9
                }
            else:
                # 낮은 협업 점수 - Gabriel 단독 실행 제안
                proposal = {
                    'summary': 'Gabriel 실행기를 통한 직접적이고 빠른 명령 실행',
                    'action': 'solo_execute',
                    'executor': 'aiin',
                    'workflow': [
                        {'step': 1, 'actor': 'aiin', 'action': '명령어 안전성 검증'},
                        {'step': 2, 'actor': 'aiin', 'action': 'Gabriel 실행기를 통한 명령 실행'},
                        {'step': 3, 'actor': 'aiin', 'action': '실행 결과 정리 및 반환'}
                    ],
                    'estimated_time': '30초-1분',
                    'confidence': 0.85
                }
            
            logger.info(f"AIIN: 최종 제안 완료 - {proposal['summary']}")
            return proposal
            
        except Exception as e:
            logger.error(f"AIIN 최종 제안 생성 오류: {str(e)}")
            return {
                'error': str(e),
                'summary': '제안 생성 중 오류 발생',
                'action': 'error'
            }
    
    async def execute_plan(self, consensus: Dict[str, Any]) -> str:
        """계획 실행"""
        try:
            logger.info(f"AIIN: 계획 실행 시작 - {consensus.get('summary', 'Unknown')}")
            
            # 실행 시뮬레이션
            workflow = consensus.get('workflow', [])
            results = []
            
            for step in workflow:
                if step.get('actor') == 'aiin':
                    await asyncio.sleep(0.3)  # Gabriel 실행은 빠름
                    step_result = await self._execute_aiin_step(step)
                    results.append(f"Step {step['step']}: {step_result}")
            
            final_result = f"AIIN Gabriel 실행기 완료.\n" + "\n".join(results)
            
            logger.info("AIIN: 계획 실행 완료")
            return final_result
            
        except Exception as e:
            logger.error(f"AIIN 계획 실행 오류: {str(e)}")
            return f"AIIN 실행 중 오류 발생: {str(e)}"
    
    async def _execute_aiin_step(self, step: Dict[str, Any]) -> str:
        """AIIN 단계 실행"""
        action = step.get('action', '')
        
        if '환경' in action or '준비' in action:
            # 실제 시스템 명령 실행 시뮬레이션
            result = await self.gabriel_executor.execute_safe_command('whoami && pwd && date')
            return f"시스템 환경 확인 완료: {result[:50]}..."
        elif '검증' in action:
            return "명령어 안전성을 검증하고 실행 준비를 완료했습니다."
        elif '실행' in action:
            # Gabriel 실행기를 통한 명령 실행
            result = await self.gabriel_executor.execute_safe_command('echo "Gabriel 실행기 작동 중..." && uptime')
            return f"Gabriel 실행 완료: {result[:100]}..."
        elif '정리' in action:
            return "실행 결과를 정리하고 사용자에게 반환할 형태로 가공했습니다."
        else:
            return f"'{action}' 작업을 Gabriel 실행기로 성공적으로 완료했습니다."
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'name': 'AIIN',
            'status': 'active',
            'tools_available': self.tools_available,
            'last_activity': datetime.now().isoformat(),
            'gabriel_status': self.gabriel_executor.get_status()
        }

    async def process_manus_response(self, manus_response: Dict[str, Any]) -> Dict[str, Any]:
        """Manus AI의 응답을 처리하고 AIIN의 다음 행동을 결정"""
        logger.info(f"AIIN: Manus AI 응답 처리 시작 - {manus_response.get("summary", "No summary")}")

        # Manus의 응답을 현재 컨텍스트에 추가
        self.current_context["manus_response"] = manus_response

        # Manus의 응답을 기반으로 AIIN의 행동 결정 로직
        if manus_response.get("action") == "propose_plan":
            # Manus가 계획을 제안한 경우, AIIN은 이를 검토하고 실행 지원 여부 결정
            plan = manus_response.get("plan", [])
            if plan:
                feedback = f"Manus AI가 {len(plan)}단계의 상세 계획을 제시했습니다. AIIN은 이 계획의 시스템 명령 실행 단계를 지원할 준비가 되어 있습니다."
                action_to_take = "review_and_support_manus_plan"
                proposed_workflow = []
                for i, step in enumerate(plan):
                    if any(keyword in step.lower() for keyword in ["파일", "시스템", "설치", "실행", "명령"]):
                        proposed_workflow.append(f"{i+1}단계 ({step}): AIIN(Gabriel)이 시스템 명령 실행 지원")
                    else:
                        proposed_workflow.append(f"{i+1}단계 ({step}): Manus가 주도적으로 작업 수행")
                return {
                    "aiin_action": action_to_take,
                    "feedback": feedback,
                    "proposed_workflow": proposed_workflow,
                    "confidence": 0.95
                }
            else:
                return {
                    "aiin_action": "request_clarification",
                    "feedback": "Manus AI가 계획을 제안했지만, 구체적인 단계가 없습니다. 계획을 명확히 해주십시오.",
                    "confidence": 0.6
                }
        elif manus_response.get("action") == "request_info":
            # Manus가 정보 요청한 경우, AIIN은 필요한 정보를 제공
            info_needed = manus_response.get("info_type", "unknown")
            if info_needed == "system_status":
                system_status = self.get_status()
                return {
                    "aiin_action": "provide_info",
                    "feedback": f"Manus AI의 시스템 상태 요청에 응답합니다. 현재 AIIN의 상태: {system_status}",
                    "info": system_status,
                    "confidence": 0.9
                }
            else:
                return {
                    "aiin_action": "cannot_provide_info",
                    "feedback": f"요청하신 정보({info_needed})는 현재 AIIN이 제공할 수 없습니다.",
                    "confidence": 0.5
                }
        elif "error" in manus_response:
            # Manus에서 오류 발생 시, AIIN이 단독으로 처리 시도
            return {
                "aiin_action": "solo_execution_attempt",
                "feedback": "Manus AI에서 오류가 발생했습니다. AIIN이 Gabriel 실행기를 통해 단독으로 작업을 시도합니다.",
                "confidence": 0.8
            }
        else:
            # 기타 Manus 응답에 대한 일반적인 처리
            return {
                "aiin_action": "acknowledge_and_wait",
                "feedback": "Manus AI의 응답을 확인했습니다. 다음 지시를 기다립니다.",
                "confidence": 0.7
            }


class GabrielExecutor:
    """Gabriel 명령 실행기"""
    
    def __init__(self):
        self.safe_commands = [
            'whoami', 'pwd', 'date', 'uptime', 'echo', 'ls', 'cat',
            'ps', 'df', 'free', 'uname', 'id', 'groups'
        ]
        self.blocked_patterns = [
            r'\brm\b.*-rf',
            r'\bsudo\s+rm\b',
            r'\breboot\b',
            r'\bshutdown\b',
            r'\bpasswd\b',
            r'\bmkfs\b',
            r'\bformat\b'
        ]
    
    async def execute_safe_command(self, command: str) -> str:
        """안전한 명령어 실행"""
        try:
            # 명령어 안전성 검증
            if not self._is_safe_command(command):
                return f"안전하지 않은 명령어입니다: {command}"
            
            # 실제 명령어 실행 (시뮬레이션)
            await asyncio.sleep(0.2)  # 실행 시간 시뮬레이션
            
            # 실제 구현에서는 subprocess를 사용
            if 'whoami' in command:
                return "ubuntu"
            elif 'pwd' in command:
                return "/home/ubuntu"
            elif 'date' in command:
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif 'uptime' in command:
                return "up 2 days, 14:32, 1 user, load average: 0.15, 0.20, 0.18"
            elif 'echo' in command:
                return command.replace('echo ', '').strip('"\\'')
            else:
                return f"명령어 '{command}' 실행 완료"
                
        except Exception as e:
            logger.error(f"Gabriel 명령 실행 오류: {str(e)}")
            return f"실행 오류: {str(e)}"
    
    def _is_safe_command(self, command: str) -> bool:
        """명령어 안전성 검사"""
        # 위험한 패턴 검사
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        # 안전한 명령어 목록 검사
        command_parts = command.split()
        if command_parts:
            base_command = command_parts[0]
            return base_command in self.safe_commands
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Gabriel 실행기 상태"""
        return {
            'active': True,
            'safe_commands_count': len(self.safe_commands),
            'last_execution': datetime.now().isoformat()
        }


class AIINNLPProcessor:
    """AIIN 자연어 처리기"""
    
    def __init__(self):
        self.korean_mappings = {
            '재시작': 'restart',
            '상태': 'status',
            '확인': 'check',
            '실행': 'run',
            '중지': 'stop',
            '시작': 'start',
            '목록': 'list',
            '정보': 'info',
            '파일': 'file',
            '디렉토리': 'directory'
        }
    
    def parse_korean_command(self, command: str) -> str:
        """한글 명령어를 영어로 변환"""
        parsed = command.lower()
        
        # AIIN 접두사 제거
        parsed = re.sub(r'aiin,?\s*', '', parsed, flags=re.IGNORECASE)
        parsed = re.sub(r'해줘|하세요|해주세요', '', parsed)
        
        # 한글-영어 매핑
        for korean, english in self.korean_mappings.items():
            parsed = parsed.replace(korean, english)
        
        return parsed.strip()


class CommandValidator:
    """명령어 검증기"""
    
    def __init__(self):
        self.safe_commands = [
            'ls', 'cat', 'echo', 'pwd', 'whoami', 'date', 'uptime',
            'ps', 'df', 'free', 'uname', 'id', 'groups'
        ]
    
    def is_safe(self, command: str) -> bool:
        """명령어 안전성 검증"""
        command_parts = command.split()
        if command_parts:
            return command_parts[0] in self.safe_commands
        return False



