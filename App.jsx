import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Send, Bot, User, Terminal, Settings, Mic, MicOff } from 'lucide-react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [selectedModel, setSelectedModel] = useState('auto')
  const [isLoading, setIsLoading] = useState(false)
  const [availableModels, setAvailableModels] = useState([])
  const [terminalHistory, setTerminalHistory] = useState([])
  const [terminalInput, setTerminalInput] = useState('')
  const [terminalLoading, setTerminalLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  
  const messagesEndRef = useRef(null)
  const terminalEndRef = useRef(null)

  // 메시지 스크롤 자동 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const scrollTerminalToBottom = () => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    scrollTerminalToBottom()
  }, [terminalHistory])

  // 사용 가능한 모델 목록 가져오기
  useEffect(() => {
    fetchAvailableModels()
  }, [])

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('/api/ai/models')
      const data = await response.json()
      if (data.status === 'success') {
        setAvailableModels(data.models)
      }
    } catch (error) {
      console.error('모델 목록 가져오기 실패:', error)
    }
  }

  // AI 채팅 메시지 전송
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          model: selectedModel
        })
      })

      const data = await response.json()

      const aiMessage = {
        id: Date.now() + 1,
        text: data.message || '응답을 받을 수 없습니다.',
        sender: 'ai',
        model: data.model,
        timestamp: new Date().toLocaleTimeString(),
        error: data.error
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: '서버 연결에 실패했습니다.',
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        error: error.message
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // 터미널 명령어 실행
  const executeCommand = async () => {
    if (!terminalInput.trim() || terminalLoading) return

    const command = {
      id: Date.now(),
      command: terminalInput,
      timestamp: new Date().toLocaleTimeString()
    }

    setTerminalHistory(prev => [...prev, command])
    setTerminalInput('')
    setTerminalLoading(true)

    try {
      const response = await fetch('/api/terminal/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: terminalInput,
          session_id: 'default'
        })
      })

      const data = await response.json()

      const result = {
        id: Date.now() + 1,
        ...data.result,
        timestamp: new Date().toLocaleTimeString()
      }

      setTerminalHistory(prev => [...prev, result])
    } catch (error) {
      const errorResult = {
        id: Date.now() + 1,
        command: terminalInput,
        output: '',
        error: `네트워크 오류: ${error.message}`,
        exit_code: 1,
        timestamp: new Date().toLocaleTimeString()
      }
      setTerminalHistory(prev => [...prev, errorResult])
    } finally {
      setTerminalLoading(false)
    }
  }

  // 음성 인식 (Web Speech API)
  const toggleVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('이 브라우저는 음성 인식을 지원하지 않습니다.')
      return
    }

    if (isListening) {
      setIsListening(false)
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.lang = 'ko-KR'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInputMessage(transcript)
      setIsListening(false)
    }

    recognition.onerror = () => {
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognition.start()
  }

  const handleKeyPress = (e, action) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      action()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold text-gray-800">
              🤖 Chavion AI Platform
            </CardTitle>
            <p className="text-center text-gray-600">
              다중 AI 모델 협업 플랫폼
            </p>
          </CardHeader>
        </Card>

        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <Bot size={16} />
              AI 채팅
            </TabsTrigger>
            <TabsTrigger value="terminal" className="flex items-center gap-2">
              <Terminal size={16} />
              웹 터미널
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings size={16} />
              설정
            </TabsTrigger>
          </TabsList>

          {/* AI 채팅 탭 */}
          <TabsContent value="chat">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>AI 채팅</CardTitle>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="모델 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">자동 선택</SelectItem>
                      {availableModels.map(model => (
                        <SelectItem key={model.id} value={model.id}>
                          {model.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96 mb-4 p-4 border rounded-lg bg-white">
                  {messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-20">
                      안녕하세요! 무엇을 도와드릴까요?
                    </div>
                  ) : (
                    messages.map(message => (
                      <div
                        key={message.id}
                        className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.sender === 'user'
                              ? 'bg-blue-500 text-white'
                              : message.error
                              ? 'bg-red-100 text-red-800 border border-red-300'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            {message.sender === 'user' ? (
                              <User size={14} />
                            ) : (
                              <Bot size={14} />
                            )}
                            <span className="text-xs opacity-75">
                              {message.timestamp}
                            </span>
                            {message.model && (
                              <Badge variant="secondary" className="text-xs">
                                {message.model}
                              </Badge>
                            )}
                          </div>
                          <p className="whitespace-pre-wrap">{message.text}</p>
                        </div>
                      </div>
                    ))
                  )}
                  {isLoading && (
                    <div className="flex justify-start mb-4">
                      <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Bot size={14} />
                          <span className="text-xs opacity-75">응답 중...</span>
                        </div>
                        <div className="flex gap-1 mt-2">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </ScrollArea>

                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => handleKeyPress(e, sendMessage)}
                    placeholder="메시지를 입력하세요..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button
                    onClick={toggleVoiceRecognition}
                    variant={isListening ? "destructive" : "outline"}
                    size="icon"
                    disabled={isLoading}
                  >
                    {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                  </Button>
                  <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                    <Send size={16} />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 웹 터미널 탭 */}
          <TabsContent value="terminal">
            <Card>
              <CardHeader>
                <CardTitle>웹 터미널</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96 mb-4 p-4 border rounded-lg bg-black text-green-400 font-mono text-sm">
                  {terminalHistory.length === 0 ? (
                    <div className="text-green-400">
                      $ 터미널에 오신 것을 환영합니다. 명령어를 입력하세요.
                    </div>
                  ) : (
                    terminalHistory.map(entry => (
                      <div key={entry.id} className="mb-2">
                        {entry.command && (
                          <div className="text-green-400">
                            $ {entry.command}
                          </div>
                        )}
                        {entry.output && (
                          <div className="text-white whitespace-pre-wrap">
                            {entry.output}
                          </div>
                        )}
                        {entry.error && (
                          <div className="text-red-400 whitespace-pre-wrap">
                            {entry.error}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  {terminalLoading && (
                    <div className="text-yellow-400">실행 중...</div>
                  )}
                  <div ref={terminalEndRef} />
                </ScrollArea>

                <div className="flex gap-2">
                  <div className="flex-1 flex items-center bg-black text-green-400 font-mono text-sm px-3 py-2 rounded border">
                    <span className="mr-2">$</span>
                    <Input
                      value={terminalInput}
                      onChange={(e) => setTerminalInput(e.target.value)}
                      onKeyPress={(e) => handleKeyPress(e, executeCommand)}
                      placeholder="명령어를 입력하세요..."
                      disabled={terminalLoading}
                      className="bg-transparent border-none text-green-400 font-mono focus:ring-0 focus:outline-none p-0"
                    />
                  </div>
                  <Button onClick={executeCommand} disabled={terminalLoading || !terminalInput.trim()}>
                    실행
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 설정 탭 */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>설정</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">사용 가능한 AI 모델</h3>
                    {availableModels.length === 0 ? (
                      <p className="text-gray-500">API 키가 설정되지 않았습니다.</p>
                    ) : (
                      <div className="space-y-2">
                        {availableModels.map(model => (
                          <div key={model.id} className="flex items-center justify-between p-3 border rounded-lg">
                            <div>
                              <h4 className="font-medium">{model.name}</h4>
                              <p className="text-sm text-gray-500">{model.provider}</p>
                            </div>
                            <Badge variant={model.status === 'available' ? 'default' : 'secondary'}>
                              {model.status === 'available' ? '사용 가능' : '사용 불가'}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-2">API 키 설정</h3>
                    <p className="text-sm text-gray-600 mb-2">
                      환경변수에서 API 키를 설정하세요:
                    </p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• OPENAI_API_KEY: OpenAI GPT 모델용</li>
                      <li>• GEMINI_API_KEY: Google Gemini 모델용</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

