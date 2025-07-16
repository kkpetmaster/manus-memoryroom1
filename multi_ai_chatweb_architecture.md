# 다중 AI 모델 채팅 웹 아키텍처 설계

## 개요

이 문서는 여러 AI 모델(Manus AI, AIIN 등)이 상주하며 서로 토론하고 합의된 결과물을 도출하는 채팅 웹 애플리케이션의 아키텍처를 설계합니다. 각 AI 모델은 독립적인 실행 환경을 가지며, 실시간으로 명령을 실행하고 그 결과를 공유하여 협업할 수 있는 시스템을 구축하는 것이 목표입니다.

## 시스템 아키텍처

### 1. 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스 (Frontend)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   채팅 인터페이스   │  │   실행 결과 뷰어   │  │   AI 상태 모니터   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   중앙 오케스트레이터 (Backend)                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   토론 관리자     │  │   합의 엔진      │  │   결과 통합기     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   Manus AI 환경      │ │   AIIN AI 환경       │ │   추가 AI 환경        │
│ ┌─────────────────┐ │ │ ┌─────────────────┐ │ │ ┌─────────────────┐ │
│ │  Manus API      │ │ │ │  AIIN 실행기     │ │ │ │  기타 AI 모델    │ │
│ │  Gateway        │ │ │ │                 │ │ │ │                 │ │
│ └─────────────────┘ │ │ └─────────────────┘ │ │ └─────────────────┘ │
│ ┌─────────────────┐ │ │ ┌─────────────────┐ │ │ ┌─────────────────┐ │
│ │  샌드박스 환경    │ │ │ │  로컬 실행 환경   │ │ │ │  독립 실행 환경   │ │
│ │  (컴퓨터 사용)    │ │ │ │  (Gabriel)      │ │ │ │                 │ │
│ └─────────────────┘ │ │ └─────────────────┘ │ │ └─────────────────┘ │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

### 2. 핵심 컴포넌트

#### 2.1 중앙 오케스트레이터 (Central Orchestrator)

중앙 오케스트레이터는 다중 AI 모델 간의 상호작용을 관리하는 핵심 컴포넌트입니다.

**주요 기능:**
- 사용자 요청 분석 및 AI 모델들에게 작업 분배
- AI 모델 간 토론 프로세스 관리
- 각 AI의 응답 수집 및 합의 도출
- 최종 결과 통합 및 사용자에게 전달

**구현 기술:**
- Node.js + Express.js 또는 Python + FastAPI
- WebSocket을 통한 실시간 통신
- Redis를 활용한 세션 및 상태 관리

#### 2.2 Manus AI 환경

Manus AI가 실제 컴퓨터 환경에서 작업을 수행할 수 있는 독립적인 실행 환경입니다.

**구성 요소:**
- **Manus API Gateway**: Manus AI의 기능을 웹 애플리케이션에서 호출할 수 있도록 하는 API 인터페이스
- **샌드박스 환경**: Manus AI가 안전하게 컴퓨터 작업을 수행할 수 있는 격리된 환경
- **도구 연동**: 파일 시스템, 웹 브라우저, 코드 실행, 이미지 생성 등 다양한 도구 접근

**기술적 구현:**
```python
# Manus AI 환경 연동 예시
class ManusEnvironment:
    def __init__(self):
        self.sandbox = DockerSandbox()
        self.tools = {
            'file_system': FileSystemTool(),
            'web_browser': BrowserTool(),
            'code_executor': CodeExecutorTool(),
            'image_generator': ImageGeneratorTool()
        }
    
    async def execute_task(self, task_description):
        # Manus AI API 호출
        response = await self.call_manus_api(task_description)
        
        # 도구 사용이 필요한 경우 실행
        if response.requires_tools:
            tool_results = await self.execute_tools(response.tool_calls)
            return await self.integrate_results(response, tool_results)
        
        return response
```

#### 2.3 AIIN AI 환경

AIIN이 Gabriel 실행기를 통해 명령을 실행할 수 있는 환경입니다.

**구성 요소:**
- **AIIN 실행기 (Gabriel)**: 기존에 구축된 AIIN의 명령 실행 시스템
- **로컬 실행 환경**: AIIN이 시스템 명령을 안전하게 실행할 수 있는 환경
- **자연어 처리 모듈**: 사용자 명령을 해석하고 적절한 시스템 명령으로 변환

**기술적 구현:**
```python
# AIIN 환경 연동 예시
class AIINEnvironment:
    def __init__(self):
        self.gabriel_executor = GabrielExecutor()
        self.nlp_processor = AIINNLPProcessor()
        self.command_validator = CommandValidator()
    
    async def execute_task(self, task_description):
        # 자연어 명령 해석
        parsed_command = self.nlp_processor.parse(task_description)
        
        # 명령 안전성 검증
        if self.command_validator.is_safe(parsed_command):
            result = await self.gabriel_executor.execute(parsed_command)
            return self.format_response(result)
        else:
            return {"error": "안전하지 않은 명령입니다."}
```

### 3. 토론 및 합의 메커니즘

#### 3.1 토론 프로세스

1. **초기 분석 단계**: 각 AI가 사용자 요청을 독립적으로 분석
2. **의견 제시 단계**: 각 AI가 자신의 접근 방법과 예상 결과를 제시
3. **토론 단계**: AI들이 서로의 의견을 검토하고 피드백 제공
4. **합의 도출 단계**: 최적의 해결책에 대한 합의 형성
5. **실행 단계**: 합의된 계획에 따라 각 AI가 역할 분담하여 실행

#### 3.2 합의 알고리즘

```python
class ConsensusEngine:
    def __init__(self):
        self.voting_weight = {
            'manus': 0.6,  # Manus AI의 가중치
            'aiin': 0.4    # AIIN의 가중치
        }
    
    async def reach_consensus(self, proposals):
        # 1. 각 제안의 실행 가능성 평가
        feasibility_scores = await self.evaluate_feasibility(proposals)
        
        # 2. 사용자 요구사항 부합도 평가
        relevance_scores = await self.evaluate_relevance(proposals)
        
        # 3. 가중 평균을 통한 최종 점수 계산
        final_scores = self.calculate_weighted_scores(
            feasibility_scores, relevance_scores
        )
        
        # 4. 최고 점수 제안 선택 또는 하이브리드 접근법 생성
        return self.select_best_approach(proposals, final_scores)
```

### 4. 실시간 통신 아키텍처

#### 4.1 WebSocket 기반 실시간 통신

```javascript
// Frontend WebSocket 연결
class MultiAIChatClient {
    constructor() {
        this.ws = new WebSocket('ws://localhost:8080/multi-ai-chat');
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'ai_response':
                    this.displayAIResponse(data.ai_name, data.content);
                    break;
                case 'discussion_update':
                    this.updateDiscussionView(data.discussion_state);
                    break;
                case 'consensus_reached':
                    this.displayConsensus(data.consensus);
                    break;
                case 'execution_result':
                    this.displayExecutionResult(data.result);
                    break;
            }
        };
    }
    
    sendUserMessage(message) {
        this.ws.send(JSON.stringify({
            type: 'user_message',
            content: message,
            timestamp: Date.now()
        }));
    }
}
```

#### 4.2 Backend WebSocket 서버

```python
# Backend WebSocket 서버 (FastAPI + WebSocket)
from fastapi import FastAPI, WebSocket
import asyncio
import json

app = FastAPI()

class MultiAIOrchestrator:
    def __init__(self):
        self.ai_environments = {
            'manus': ManusEnvironment(),
            'aiin': AIINEnvironment()
        }
        self.consensus_engine = ConsensusEngine()
        self.active_sessions = {}
    
    async def handle_user_message(self, websocket: WebSocket, message: str):
        session_id = id(websocket)
        
        # 1. 각 AI에게 메시지 전달 및 초기 응답 수집
        ai_responses = await self.collect_initial_responses(message)
        
        # 2. 토론 프로세스 시작
        discussion_result = await self.facilitate_discussion(ai_responses)
        
        # 3. 합의 도출
        consensus = await self.consensus_engine.reach_consensus(discussion_result)
        
        # 4. 합의된 계획 실행
        execution_result = await self.execute_consensus_plan(consensus)
        
        # 5. 최종 결과 전달
        await websocket.send_text(json.dumps({
            'type': 'final_result',
            'result': execution_result
        }))

@app.websocket("/multi-ai-chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    orchestrator = MultiAIOrchestrator()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data['type'] == 'user_message':
                await orchestrator.handle_user_message(
                    websocket, message_data['content']
                )
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

### 5. 보안 및 안전성

#### 5.1 샌드박스 격리

각 AI 환경은 Docker 컨테이너 또는 가상 머신을 통해 격리되어 시스템 보안을 보장합니다.

```yaml
# Docker Compose 설정 예시
version: '3.8'
services:
  manus-environment:
    build: ./manus-env
    volumes:
      - manus-sandbox:/workspace
    networks:
      - ai-network
    security_opt:
      - no-new-privileges:true
    
  aiin-environment:
    build: ./aiin-env
    volumes:
      - aiin-sandbox:/workspace
    networks:
      - ai-network
    security_opt:
      - no-new-privileges:true
  
  orchestrator:
    build: ./orchestrator
    ports:
      - "8080:8080"
    networks:
      - ai-network
    depends_on:
      - manus-environment
      - aiin-environment

volumes:
  manus-sandbox:
  aiin-sandbox:

networks:
  ai-network:
    driver: bridge
```

#### 5.2 명령 실행 제한

```python
class SecurityManager:
    def __init__(self):
        self.allowed_commands = {
            'file_operations': ['ls', 'cat', 'mkdir', 'touch'],
            'system_info': ['whoami', 'date', 'uptime'],
            'development': ['npm', 'python', 'node']
        }
        self.blocked_patterns = [
            r'rm\s+-rf',
            r'sudo\s+rm',
            r'format\s+',
            r'del\s+/[sq]'
        ]
    
    def validate_command(self, command: str) -> bool:
        # 위험한 명령 패턴 검사
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        # 허용된 명령어 검사
        command_parts = command.split()
        if command_parts and command_parts[0] in self.get_all_allowed_commands():
            return True
        
        return False
```

이 아키텍처를 통해 마스터님이 원하시는 다중 AI 모델 채팅 웹을 구축할 수 있습니다. 각 AI가 독립적인 실행 환경을 가지면서도 서로 협업하여 더 나은 결과를 도출하는 시스템이 될 것입니다.

