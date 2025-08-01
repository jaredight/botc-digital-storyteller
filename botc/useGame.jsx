import { createContext, useContext, useState, useEffect } from 'react'

const GameContext = createContext()

export function useGame() {
  const context = useContext(GameContext)
  if (!context) {
    throw new Error('useGame must be used within a GameProvider')
  }
  return context
}

export function GameProvider({ children }) {
  const [currentGame, setCurrentGame] = useState(null)
  const [scripts, setScripts] = useState([])
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(false)

  // API base URL
  const API_BASE = '/api'

  useEffect(() => {
    loadScripts()
    loadRoles()
  }, [])

  const loadScripts = async () => {
    try {
      const response = await fetch(`${API_BASE}/scripts?include_roles=true`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setScripts(data.scripts)
      }
    } catch (error) {
      console.error('Failed to load scripts:', error)
    }
  }

  const loadRoles = async () => {
    try {
      const response = await fetch(`${API_BASE}/roles`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setRoles(data.roles)
      }
    } catch (error) {
      console.error('Failed to load roles:', error)
    }
  }

  const createGame = async (scriptId, settings = {}) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          script_id: scriptId,
          settings
        })
      })

      const data = await response.json()

      if (response.ok) {
        setCurrentGame(data.game)
        return { success: true, game: data.game }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to create game:', error)
      return { success: false, error: 'Network error occurred' }
    } finally {
      setLoading(false)
    }
  }

  const joinGame = async (joinCode) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/games/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ join_code: joinCode })
      })

      const data = await response.json()

      if (response.ok) {
        setCurrentGame(data.game)
        return { success: true, game: data.game }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to join game:', error)
      return { success: false, error: 'Network error occurred' }
    } finally {
      setLoading(false)
    }
  }

  const leaveGame = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/leave`, {
        method: 'POST',
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        setCurrentGame(null)
        return { success: true }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to leave game:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const getGame = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}`, {
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        setCurrentGame(data.game)
        return { success: true, game: data.game }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to get game:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const toggleReady = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/ready`, {
        method: 'POST',
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        // Refresh game state
        await getGame(gameId)
        return { success: true, isReady: data.is_ready }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to toggle ready:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const startGame = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/start`, {
        method: 'POST',
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        setCurrentGame(data.game)
        return { success: true, game: data.game }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to start game:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const submitVote = async (gameId, targetId, voteType = 'execution') => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          target_id: targetId,
          vote_type: voteType
        })
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, vote: data.vote }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to submit vote:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const nominatePlayer = async (gameId, targetId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/nominate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ target_id: targetId })
      })

      const data = await response.json()

      if (response.ok) {
        // Refresh game state
        await getGame(gameId)
        return { success: true, nominations: data.nominations }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to nominate player:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const getGameHistory = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/history`, {
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, history: data.history }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to get game history:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const getRoleDistribution = async (scriptId, playerCount) => {
    try {
      const response = await fetch(`${API_BASE}/scripts/${scriptId}/distribution/${playerCount}`, {
        credentials: 'include'
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, distribution: data }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Failed to get role distribution:', error)
      return { success: false, error: 'Network error occurred' }
    }
  }

  const value = {
    currentGame,
    scripts,
    roles,
    loading,
    createGame,
    joinGame,
    leaveGame,
    getGame,
    toggleReady,
    startGame,
    submitVote,
    nominatePlayer,
    getGameHistory,
    getRoleDistribution,
    loadScripts,
    loadRoles
  }

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  )
}

