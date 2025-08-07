import { createContext, useContext, useEffect, useState } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from './useAuth'

const SocketContext = createContext()

export function useSocket() {
  const context = useContext(SocketContext)
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null)
  const [connected, setConnected] = useState(false)
  const [gameUpdates, setGameUpdates] = useState([])
  const [chatMessages, setChatMessages] = useState([])
  const [playerActions, setPlayerActions] = useState([])
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      // Initialize socket connection when user is authenticated
      // autoConnect: true,
      const newSocket = io(window.location.origin, {
        withCredentials: true,
        autoConnect: true,
        // transports: ['websocket', 'polling']
        transports: ['polling']
      })

      newSocket.on('connect', () => {
        console.log('Connected to server')
        setConnected(true)
      })

      newSocket.on('disconnect', () => {
        console.log('Disconnected from server')
        setConnected(false)
      })

      newSocket.on('connected', (data) => {
        console.log('Server connection confirmed:', data.message)
      })

      newSocket.on('game_updated', (data) => {
        console.log('Game update received:', data)
        setGameUpdates(prev => [...prev, data])
      })

      newSocket.on('chat_message', (data) => {
        console.log('Chat message received:', data)
        setChatMessages(prev => [...prev, data])
      })

      newSocket.on('player_action', (data) => {
        console.log('Player action received:', data)
        setPlayerActions(prev => [...prev, data])
      })

      newSocket.on('storyteller_update', (data) => {
        console.log('Storyteller update received:', data)
        // Handle storyteller updates (phase changes, night actions, etc.)
      })

      newSocket.on('night_action_received', (data) => {
        console.log('Night action received:', data)
        // Handle night actions for storyteller
      })

      setSocket(newSocket)

      return () => {
        newSocket.close()
      }
    } else {
      // Disconnect socket when user logs out
      if (socket) {
        socket.close()
        setSocket(null)
        setConnected(false)
      }
    }
  }, [user])

  const joinGame = (gameId) => {
    if (socket && gameId) {
      socket.emit('join_game', { game_id: gameId })
      console.log(`Joining game ${gameId}`)
    }
  }

  const leaveGame = (gameId) => {
    if (socket && gameId) {
      socket.emit('leave_game', { game_id: gameId })
      console.log(`Leaving game ${gameId}`)
    }
  }

  const sendGameUpdate = (gameId, type, data) => {
    if (socket && gameId) {
      socket.emit('game_update', {
        game_id: gameId,
        type,
        data
      })
    }
  }

  const sendChatMessage = (gameId, message) => {
    if (socket && gameId && message && user) {
      socket.emit('chat_message', {
        game_id: gameId,
        message,
        username: user.username
      })
    }
  }

  const sendPlayerAction = (gameId, actionType, actionData) => {
    if (socket && gameId && actionType) {
      socket.emit('player_action', {
        game_id: gameId,
        action_type: actionType,
        action_data: actionData
      })
    }
  }

  const sendNightAction = (gameId, playerId, actionType, targetId) => {
    if (socket && gameId && playerId && actionType) {
      socket.emit('night_action', {
        game_id: gameId,
        player_id: playerId,
        action_type: actionType,
        target_id: targetId
      })
    }
  }

  const sendStorytellerUpdate = (gameId, type, data) => {
    if (socket && gameId && type) {
      socket.emit('storyteller_update', {
        game_id: gameId,
        type,
        data
      })
    }
  }

  const clearGameUpdates = () => {
    setGameUpdates([])
  }

  const clearChatMessages = () => {
    setChatMessages([])
  }

  const clearPlayerActions = () => {
    setPlayerActions([])
  }

  const getGameMessages = (gameId) => {
    return chatMessages.filter(msg => msg.game_id === gameId)
  }

  const getGameActions = (gameId) => {
    return playerActions.filter(action => action.game_id === gameId)
  }

  const getGameUpdates = (gameId) => {
    return gameUpdates.filter(update => update.game_id === gameId)
  }

  const value = {
    socket,
    connected,
    gameUpdates,
    chatMessages,
    playerActions,
    joinGame,
    leaveGame,
    sendGameUpdate,
    sendChatMessage,
    sendPlayerAction,
    sendNightAction,
    sendStorytellerUpdate,
    clearGameUpdates,
    clearChatMessages,
    clearPlayerActions,
    getGameMessages,
    getGameActions,
    getGameUpdates
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}

