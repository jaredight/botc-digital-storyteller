import { useState, useEffect, useRef } from 'react'
import { useSocket } from '../hooks/useSocket'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { MessageSquare, Send, Users, Clock } from 'lucide-react'

export default function GameChat({ gameId, isVisible = true }) {
  const { user } = useAuth()
  const { connected, chatMessages, sendChatMessage } = useSocket()
  const [message, setMessage] = useState('')
  const [localMessages, setLocalMessages] = useState([])
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Filter messages for this game and update local state
    const gameMessages = chatMessages.filter(msg => 
      msg.game_id === gameId || !msg.game_id // Include global messages
    )
    setLocalMessages(gameMessages)
  }, [chatMessages, gameId])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    scrollToBottom()
  }, [localMessages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (message.trim() && connected && user) {
      sendChatMessage(gameId, message.trim())
      setMessage('')
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getMessageType = (msg) => {
    if (msg.type === 'system') return 'system'
    if (msg.type === 'whisper') return 'whisper'
    if (msg.type === 'storyteller') return 'storyteller'
    return 'normal'
  }

  const getMessageStyle = (msg) => {
    const type = getMessageType(msg)
    switch (type) {
      case 'system':
        return 'bg-slate-700/50 border-l-4 border-blue-400 text-blue-200'
      case 'whisper':
        return 'bg-purple-900/30 border-l-4 border-purple-400 text-purple-200'
      case 'storyteller':
        return 'bg-yellow-900/30 border-l-4 border-yellow-400 text-yellow-200'
      default:
        return 'bg-slate-800/50'
    }
  }

  if (!isVisible) return null

  return (
    <Card className="bg-slate-800/50 border-slate-700 h-96 flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center">
          <MessageSquare className="mr-2 h-5 w-5" />
          Game Chat
          {!connected && (
            <Badge variant="destructive" className="ml-2">
              Disconnected
            </Badge>
          )}
        </CardTitle>
        <CardDescription className="text-slate-300">
          Communicate with other players
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages Area */}
        <ScrollArea className="flex-1 px-4">
          <div className="space-y-2 pb-4">
            {localMessages.length === 0 ? (
              <div className="text-center text-slate-400 py-8">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No messages yet. Start the conversation!</p>
              </div>
            ) : (
              localMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${getMessageStyle(msg)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-white">
                          {msg.username || 'System'}
                        </span>
                        {msg.type && msg.type !== 'normal' && (
                          <Badge variant="outline" className="text-xs">
                            {msg.type}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-slate-200 break-words">
                        {msg.message}
                      </p>
                    </div>
                    <div className="flex items-center text-xs text-slate-400 ml-2">
                      <Clock className="h-3 w-3 mr-1" />
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Message Input */}
        <div className="border-t border-slate-700 p-4">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={connected ? "Type a message..." : "Connecting..."}
              disabled={!connected}
              className="flex-1 bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
              maxLength={500}
            />
            <Button
              type="submit"
              disabled={!connected || !message.trim()}
              size="sm"
              className="bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
          
          {/* Connection Status */}
          <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                connected ? 'bg-green-400' : 'bg-red-400'
              }`} />
              {connected ? 'Connected' : 'Disconnected'}
            </div>
            <div>
              {message.length}/500
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

