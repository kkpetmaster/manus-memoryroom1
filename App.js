import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState('대기 중');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const executeCommand = async (command) => {
    setIsExecuting(true);
    setExecutionStatus(`명령 실행 중: ${command}`);
    
    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });
      
      const result = await response.json();
      
      setMessages(prev => [...prev, {
        type: 'system',
        content: `실행 결과: ${result.output || result.message}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      setExecutionStatus('실행 완료');
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: `오류 발생: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
      setExecutionStatus('오류 발생');
    } finally {
      setIsExecuting(false);
      setTimeout(() => setExecutionStatus('대기 중'), 2000);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isExecuting) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);

    // AIIN 명령어 처리
    if (inputValue.toLowerCase().includes('aiin') || inputValue.startsWith('/')) {
      executeCommand(inputValue);
    } else {
      // 일반 채팅 응답
      setTimeout(() => {
        setMessages(prev => [...prev, {
          type: 'ai',
          content: `안녕하세요! "${inputValue}"에 대한 응답입니다. AIIN 명령어를 사용하려면 "AIIN, [명령어]" 형식으로 입력해주세요.`,
          timestamp: new Date().toLocaleTimeString()
        }]);
      }, 500);
    }

    setInputValue('');
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AIIN 채팅웹</h1>
          <div className="status-indicator">
            <div className={`status-dot ${isExecuting ? 'executing' : 'ready'}`}></div>
            <span className="status-text">{executionStatus}</span>
          </div>
        </div>
        
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                <span className="message-text">{message.content}</span>
                <span className="message-time">{message.timestamp}</span>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="메시지를 입력하세요... (예: AIIN, nginx 재시작해줘)"
            className="message-input"
            disabled={isExecuting}
          />
          <button type="submit" disabled={isExecuting || !inputValue.trim()} className="send-button">
            {isExecuting ? '실행 중...' : '전송'}
          </button>
        </form>
      </div>

      <div className="execution-panel">
        <h3>Gabriel 실행기</h3>
        <div className="execution-status">
          <div className={`execution-indicator ${isExecuting ? 'active' : ''}`}>
            {isExecuting ? '🔄 실행 중' : '⏸️ 대기 중'}
          </div>
          <div className="execution-log">
            <p>상태: {executionStatus}</p>
            <p>마지막 업데이트: {new Date().toLocaleTimeString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

