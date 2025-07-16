# OpenAI Assistants API를 활용한 GPTs 기능 웹 통합 가이드

## 1. 개요

이 문서는 OpenAI Assistants API를 사용하여 기존 GPTs의 기능을 웹 애플리케이션(chavion.com)에 통합하는 방법을 안내합니다. 현재 OpenAI GPTs는 API 호출 없이 웹사이트에 직접 임베드하는 것을 공식적으로 지원하지 않으므로, Assistants API는 GPTs의 핵심 기능을 웹 환경에서 구현하기 위한 가장 강력하고 유연한 대안입니다. 이 가이드는 Assistants API의 주요 개념, 통합 단계, 그리고 Python을 사용한 예시를 포함합니다.

## 2. OpenAI Assistants API란?

OpenAI Assistants API는 개발자가 자체 애플리케이션 내에서 AI 어시스턴트를 구축하고 관리할 수 있도록 설계된 강력한 도구입니다. 이는 기존 GPT 모델 위에 계층화되어 있으며, 다음과 같은 핵심 기능을 제공합니다:

*   **Assistant**: 특정 목적을 위해 구성된 AI 모델입니다. Instructions(지침), 모델(예: `gpt-4o`), 도구(Code Interpreter, Retrieval, Function Calling), 그리고 Knowledge(파일)를 포함합니다.
*   **Thread**: 사용자와 어시스턴트 간의 대화 세션을 나타냅니다. 대화 기록을 자동으로 관리하여 컨텍스트를 유지합니다.
*   **Message**: Thread 내에서 사용자와 어시스턴트가 주고받는 텍스트, 이미지, 파일 등의 콘텐츠입니다.
*   **Run**: Assistant가 Thread 내의 Message에 응답을 생성하기 위해 수행하는 일련의 작업입니다. 도구 사용, 응답 생성 등의 단계를 포함합니다.

**GPTs와 Assistants API의 관계**: GPTs는 ChatGPT 인터페이스 내에서 Assistants API의 기능을 사용자 친화적인 방식으로 추상화하여 제공하는 것입니다. 따라서 GPTs를 만들 때 설정했던 Instructions, Knowledge 파일, 그리고 사용했던 도구들은 Assistants API를 통해 웹 애플리케이션에서 거의 동일하게 재현할 수 있습니다.

## 3. 통합의 필요성 및 이점

마스터님께서 API 호출 없이 GPTs를 웹에 상주시키고자 하는 목표를 가지고 계시지만, 현재로서는 Assistants API를 통한 통합이 가장 현실적인 대안입니다. 이 방법은 다음과 같은 이점을 제공합니다:

*   **기능 재현**: GPTs에서 설정했던 복잡한 지침, 파일 기반 지식 검색(Retrieval), 코드 실행(Code Interpreter) 등의 기능을 웹 애플리케이션에서 그대로 사용할 수 있습니다.
*   **확장성**: 사용자 수가 증가하거나 기능이 확장될 때 API를 통해 유연하게 대응할 수 있습니다.
*   **맞춤형 UI/UX**: 웹 애플리케이션의 디자인과 사용자 경험에 맞춰 AI 챗봇 인터페이스를 자유롭게 커스터마이징할 수 있습니다.
*   **데이터 관리**: 대화 기록 및 사용자 데이터를 자체 서버에서 관리할 수 있어 보안 및 프라이버시 측면에서 유리합니다.

## 4. 통합 단계

OpenAI Assistants API를 웹 애플리케이션에 통합하는 과정은 크게 다음과 같은 단계로 나눌 수 있습니다.

### 4.1. OpenAI API 키 설정

가장 먼저 OpenAI API 키를 발급받아야 합니다. 이 키는 API 호출 시 인증에 사용됩니다. OpenAI 플랫폼 웹사이트에서 발급받을 수 있으며, 보안을 위해 환경 변수로 관리하는 것이 좋습니다.

### 4.2. Assistant 생성 및 구성

GPTs를 만들 때 설정했던 Instructions, 모델, 그리고 도구(Code Interpreter, Retrieval, Function Calling)를 기반으로 Assistant를 생성합니다. Knowledge 파일이 있다면, 해당 파일들을 업로드하여 Assistant에 연결합니다.

### 4.3. 웹 애플리케이션 백엔드 개발

사용자의 요청을 받아 Assistants API와 통신하고, 응답을 사용자에게 전달하는 백엔드 로직을 구현합니다. Python, Node.js, Go 등 선호하는 언어와 프레임워크를 사용할 수 있습니다. 이 가이드에서는 Python Flask를 예시로 사용합니다.

### 4.4. 웹 애플리케이션 프론트엔드 개발

사용자가 AI 어시스턴트와 상호작용할 수 있는 채팅 인터페이스를 구축합니다. 백엔드 API와 통신하여 메시지를 주고받고, 응답을 화면에 표시합니다.

### 4.5. 배포

개발된 백엔드 및 프론트엔드 애플리케이션을 서버에 배포하여 chavion.com 도메인에서 접근할 수 있도록 합니다.

## 5. Python을 사용한 Assistants API 통합 예시 (백엔드)

다음은 Python Flask를 사용하여 Assistants API와 연동하는 간단한 백엔드 예시 코드입니다. 이 코드는 사용자의 메시지를 받아 Assistant에 전달하고, Assistant의 응답을 다시 사용자에게 반환하는 기본적인 흐름을 보여줍니다.

```python
import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Assistant ID 설정 (미리 생성된 Assistant의 ID를 사용)
#    GPTs의 Instructions, Knowledge, Tools를 기반으로 Assistant를 생성해야 합니다.
#    생성 방법은 OpenAI Assistants Playground 또는 API 문서를 참조하세요.
ASSISTANT_ID = "your_assistant_id_here" # 여기에 실제 Assistant ID를 입력하세요.

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    thread_id = request.json.get('thread_id') # 기존 스레드가 있다면 사용

    if not user_message:
        return jsonify({"error": "메시지를 입력해주세요."}), 400

    try:
        # 2. 스레드 생성 또는 로드
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
        else:
            thread = client.beta.threads.retrieve(thread_id)

        # 3. 스레드에 메시지 추가
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )

        # 4. Assistant 실행 (Run 생성)
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        )

        # 5. Run 완료 대기 및 응답 가져오기
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            # 필요에 따라 Tool Calls 처리 로직 추가
            # if run.status == "requires_action":
            #     handle_tool_calls(run, thread_id)
            asyncio.sleep(0.5) # 짧은 지연

        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )

        # 최신 Assistant 응답 찾기
        assistant_response = ""
        for msg in reversed(messages.data):
            if msg.role == "assistant" and msg.run_id == run.id:
                for content_block in msg.content:
                    if content_block.type == "text":
                        assistant_response = content_block.text.value
                        break
                break

        return jsonify({"response": assistant_response, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**코드 설명:**

*   `ASSISTANT_ID`: OpenAI 플랫폼에서 미리 생성한 Assistant의 ID를 입력해야 합니다. 이 Assistant는 마스터님의 GPTs와 동일한 Instructions, Knowledge, Tools 설정을 가져야 합니다.
*   `/chat` 엔드포인트: 사용자의 메시지를 `message` 필드로 받고, 선택적으로 `thread_id`를 받아 기존 대화를 이어갈 수 있도록 합니다.
*   **스레드 관리**: `thread_id`가 없으면 새로운 스레드를 생성하고, 있으면 기존 스레드를 로드합니다.
*   **메시지 추가**: 사용자의 메시지를 스레드에 추가합니다.
*   **Assistant 실행**: `client.beta.threads.runs.create`를 호출하여 Assistant가 메시지에 응답하도록 실행합니다.
*   **응답 대기**: `run.status`가 `completed`가 될 때까지 기다립니다. 실제 애플리케이션에서는 웹훅(Webhook)이나 비동기 처리(Long Polling)를 사용하여 효율적으로 처리하는 것이 좋습니다.
*   **응답 추출**: Run이 완료되면 스레드의 메시지 목록에서 최신 Assistant의 응답을 추출하여 반환합니다.

## 6. 프론트엔드 통합 (개념)

프론트엔드(chavion.com의 채팅 웹)에서는 다음과 같은 방식으로 백엔드와 통신합니다.

1.  **메시지 입력**: 사용자가 채팅 입력란에 메시지를 입력합니다.
2.  **백엔드 호출**: JavaScript(Fetch API 또는 Axios 등)를 사용하여 백엔드의 `/chat` 엔드포인트로 사용자 메시지를 POST 요청으로 보냅니다. 이때 `thread_id`를 함께 보내어 대화 컨텍스트를 유지합니다.
3.  **응답 처리**: 백엔드로부터 받은 응답(`response`와 `thread_id`)을 채팅 UI에 표시합니다.

**예시 (JavaScript - Fetch API):**

```javascript
async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value;
    if (!message) return;

    // 채팅 UI에 사용자 메시지 추가
    appendMessage('user', message);
    userInput.value = '';

    const threadId = localStorage.getItem('current_thread_id'); // 로컬 스토리지에서 스레드 ID 가져오기

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, thread_id: threadId }),
        });

        const data = await response.json();

        if (data.error) {
            appendMessage('system', `오류: ${data.error}`);
        } else {
            appendMessage('assistant', data.response);
            localStorage.setItem('current_thread_id', data.thread_id); // 새 스레드 ID 저장
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage('system', '메시지를 보내는 중 오류가 발생했습니다.');
    }
}

function appendMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add(sender);
    messageElement.textContent = text;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 스크롤 하단으로 이동
}

// 초기 로드 시 스레드 ID 초기화 (필요한 경우)
// localStorage.removeItem('current_thread_id');
```

## 7. 다음 단계

1.  **Assistant 생성**: OpenAI 플랫폼(platform.openai.com)에서 마스터님의 GPTs와 동일한 Instructions, Knowledge 파일, 도구를 사용하여 Assistant를 생성하고 `ASSISTANT_ID`를 확보합니다.
2.  **백엔드 구현**: 위에 제시된 Python Flask 예시 코드를 기반으로 백엔드 서버를 구축합니다. `OPENAI_API_KEY` 환경 변수를 설정하는 것을 잊지 마십시오.
3.  **프론트엔드 통합**: chavion.com의 채팅 웹에 JavaScript 코드를 추가하여 백엔드와 통신하는 채팅 인터페이스를 구현합니다.
4.  **배포**: 개발된 백엔드와 프론트엔드를 서버에 배포합니다.

이 과정에서 도움이 필요하시면 언제든지 말씀해주세요. 특히 백엔드 코드 작성이나 배포 과정에서 제가 직접 지원해 드릴 수 있는 부분이 있을 것입니다.

---

