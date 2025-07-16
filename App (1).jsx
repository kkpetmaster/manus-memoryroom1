import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Avatar, AvatarFallback } from '@/components/ui/avatar.jsx'
import { Send, Bot, User, Cpu, MessageSquare, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import io from 'socket.io-client'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [aiStatuses, setAiStatuses] = useState({
    manus: { status: 'idle', lastActivity: null },
    aiin: { status: 'idle', lastActivity: null }
  })
  const [discussionState, setDiscussionState] = useState('waiting') // waiting, analyzing, discussing, consensus, executing
  const socketRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Socket.IO 연결 설정
    const connectSocket = () => {
      try {
        socketRef.current = io('http://localhost:8080', {
          transports: ['websocket', 'polling']
        })
        
        socketRef.current.on('connect', () => {
          setIsConnected(true)
          console.log('Socket.IO 연결됨')
        })
        
        socketRef.current.on('connected', (data) => {
          console.log('서버 연결 확인:', data.message)
        })
        
        socketRef.current.on('ai_response', (data) => {
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'ai',
            sender: data.ai_name,
            content: data.content,
            timestamp: new Date()
          }])
          updateAIStatus(data.ai_name, 'active')
        })
        
        socketRef.current.on('discussion_update', (data) => {
          setDiscussionState(data.discussion_state)
          if (data.discussion_content) {
            setMessages(prev => [...prev, {
              id: Date.now() + Math.random(),
              type: 'discussion',
              content: data.discussion_content,
              timestamp: new Date()
            }])
          }
        })
        
        socketRef.current.on('consensus_reached', (data) => {
          setDiscussionState('consensus')
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'consensus',
            content: data.consensus,
            timestamp: new Date()
          }])
        })
        
        socketRef.current.on('execution_result', (data) => {
          setDiscussionState('completed')
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'result',
            content: data.result,
            timestamp: new Date()
          }])
          updateAllAIStatus('idle')
        })
        
        socketRef.current.on('error', (data) => {
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'error',
            content: data.message,
            timestamp: new Date()
          }])
          setDiscussionState('error')
          updateAllAIStatus('idle')
        })
        
        socketRef.current.on('disconnect', () => {
          setIsConnected(false)
          console.log('Socket.IO 연결 끊어짐')
        })
        
        socketRef.current.on('connect_error', (error) => {
          console.error('Socket.IO 연결 오류:', error)
          setIsConnected(false)
        })
        
      } catch (error) {
        console.error('Socket.IO 초기화 실패:', error)
      }
    }

    connectSocket()

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const updateAIStatus = (aiName, status) => {
    setAiStatuses(prev => ({
      ...prev,
      [aiName]: {
        status,
        lastActivity: new Date()
      }
    }))
  }

  const updateAllAIStatus = (status) => {
    setAiStatuses(prev => {
      const updated = {}
      Object.keys(prev).forEach(ai => {
        updated[ai] = {
          status,
          lastActivity: new Date()
        }
      })
      return updated
    })
  }

  const sendMessage = () => {
    if (!inputMessage.trim() || !isConnected) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setDiscussionState('analyzing')
    updateAllAIStatus('thinking')

    // Socket.IO로 메시지 전송
    socketRef.current.emit('user_message', {
      content: inputMessage,
      timestamp: Date.now()
    })

    setInputMessage('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'thinking':
      case 'active':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'idle':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Cpu className="w-4 h-4 text-gray-400" />
    }
  }

  const getDiscussionStateText = () => {
    switch (discussionState) {
      case 'analyzing':
        return '분석 중...'
      case 'discussing':
        return 'AI들이 토론 중...'
      case 'consensus':
        return '합의 도달'
      case 'executing':
        return '실행 중...'
      case 'completed':
        return '완료'
      case 'error':
        return '오류 발생'
      default:
        return '대기 중'
    }
  }

  const renderMessage = (message) => {
    const isUser = message.type === 'user'
    
    return (
      <div key={message.id} className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
        {!isUser && (
          <Avatar className="w-8 h-8">
            <AvatarFallback className={`text-xs ${
              message.sender === 'manus' ? 'bg-blue-100 text-blue-700' :
              message.sender === 'aiin' ? 'bg-green-100 text-green-700' :
              message.type === 'discussion' ? 'bg-purple-100 text-purple-700' :
              message.type === 'consensus' ? 'bg-orange-100 text-orange-700' :
              message.type === 'result' ? 'bg-emerald-100 text-emerald-700' :
              'bg-red-100 text-red-700'
            }`}>
              {message.sender === 'manus' ? 'M' :
               message.sender === 'aiin' ? 'A' :
               message.type === 'discussion' ? 'D' :
               message.type === 'consensus' ? 'C' :
               message.type === 'result' ? 'R' : 'E'}
            </AvatarFallback>
          </Avatar>
        )}
        
        <div className={`max-w-[70%] ${isUser ? 'order-first' : ''}`}>
          <div className={`rounded-lg p-3 ${
            isUser ? 'bg-blue-500 text-white ml-auto' :
            message.type === 'discussion' ? 'bg-purple-50 border border-purple-200' :
            message.type === 'consensus' ? 'bg-orange-50 border border-orange-200' :
            message.type === 'result' ? 'bg-emerald-50 border border-emerald-200' :
            message.type === 'error' ? 'bg-red-50 border border-red-200' :
            'bg-gray-50 border border-gray-200'
          }`}>
            {!isUser && message.sender && (
              <div className="text-xs font-medium mb-1 opacity-70">
                {message.sender === 'manus' ? 'Manus AI' :
                 message.sender === 'aiin' ? 'AIIN' :
                 message.type === 'discussion' ? '토론' :
                 message.type === 'consensus' ? '합의' :
                 message.type === 'result' ? '실행 결과' : '오류'}
              </div>
            )}
            <div className="text-sm whitespace-pre-wrap">{message.content}</div>
            <div className={`text-xs mt-1 opacity-50 ${isUser ? 'text-right' : 'text-left'}`}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
        
        {isUser && (
          <Avatar className="w-8 h-8">
            <AvatarFallback className="bg-blue-100 text-blue-700 text-xs">
              <User className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 h-screen">
        {/* 메인 채팅 영역 */}
        <div className="lg:col-span-3">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  다중 AI 채팅
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant={isConnected ? 'default' : 'destructive'}>
                    {isConnected ? '연결됨' : '연결 끊어짐'}
                  </Badge>
                  <Badge variant="outline">
                    {getDiscussionStateText()}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea className="flex-1 px-4">
                <div className="space-y-4 py-4">
                  {messages.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">
                      <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>AI들과 대화를 시작해보세요!</p>
                      <p className="text-sm mt-2">여러 AI가 협력하여 최적의 답변을 제공합니다.</p>
                    </div>
                  ) : (
                    messages.map(renderMessage)
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
              
              <Separator />
              
              <div className="p-4">
                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    disabled={!isConnected}
                    className="flex-1"
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={!inputMessage.trim() || !isConnected}
                    size="icon"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI 상태 모니터 */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">AI 상태</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(aiStatuses).map(([aiName, status]) => (
                <div key={aiName} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                  <div className="flex items-center gap-2">
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className={`text-xs ${
                        aiName === 'manus' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                      }`}>
                        {aiName === 'manus' ? 'M' : 'A'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-medium text-sm">
                        {aiName === 'manus' ? 'Manus AI' : 'AIIN'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {status.lastActivity ? 
                          `마지막 활동: ${status.lastActivity.toLocaleTimeString()}` : 
                          '활동 없음'
                        }
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {getStatusIcon(status.status)}
                    <span className="text-xs capitalize">{status.status}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">토론 진행 상황</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className={`flex items-center gap-2 p-2 rounded ${
                  discussionState === 'analyzing' ? 'bg-blue-50 text-blue-700' : 'text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    discussionState === 'analyzing' ? 'bg-blue-500' : 'bg-gray-300'
                  }`} />
                  <span className="text-sm">초기 분석</span>
                </div>
                
                <div className={`flex items-center gap-2 p-2 rounded ${
                  discussionState === 'discussing' ? 'bg-purple-50 text-purple-700' : 'text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    discussionState === 'discussing' ? 'bg-purple-500' : 'bg-gray-300'
                  }`} />
                  <span className="text-sm">AI 토론</span>
                </div>
                
                <div className={`flex items-center gap-2 p-2 rounded ${
                  discussionState === 'consensus' ? 'bg-orange-50 text-orange-700' : 'text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    discussionState === 'consensus' ? 'bg-orange-500' : 'bg-gray-300'
                  }`} />
                  <span className="text-sm">합의 도출</span>
                </div>
                
                <div className={`flex items-center gap-2 p-2 rounded ${
                  discussionState === 'executing' ? 'bg-emerald-50 text-emerald-700' : 'text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    discussionState === 'executing' ? 'bg-emerald-500' : 'bg-gray-300'
                  }`} />
                  <span className="text-sm">실행</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default App

