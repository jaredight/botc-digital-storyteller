import { useState, useEffect } from 'react'
import { useAuth } from './useAuth'

const API_BASE = 'http://localhost:5000/api'

export function useGameState() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const saveGameState = async (gameId, stateName) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          state_name: stateName
        })
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, gameState: data.game_state }
      } else {
        setError(data.error || 'Failed to save game state')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while saving game state'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const loadGameState = async (gameId, stateId) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/load/${stateId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Failed to load game state')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while loading game state'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const getGameStates = async (gameId) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/states`, {
        method: 'GET',
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, states: data.states }
      } else {
        setError(data.error || 'Failed to get game states')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while getting game states'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const createAutoSave = async (gameId) => {
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/auto-save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, gameState: data.game_state }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      return { success: false, error: 'Network error while creating auto-save' }
    }
  }

  const getGameActions = async (gameId, limit = 50) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/actions?limit=${limit}`, {
        method: 'GET',
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, actions: data.actions }
      } else {
        setError(data.error || 'Failed to get game actions')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while getting game actions'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const undoAction = async (gameId, actionId, reason = '') => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/actions/${actionId}/undo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          reason: reason
        })
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Failed to undo action')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while undoing action'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const finishGame = async (gameId, winnerTeam) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/finish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          winner_team: winnerTeam
        })
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, message: data.message, history: data.history }
      } else {
        setError(data.error || 'Failed to finish game')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while finishing game'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const getGameHistory = async (gameId, includeFull = false) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/history?full=${includeFull}`, {
        method: 'GET',
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, history: data.history }
      } else {
        setError(data.error || 'Failed to get game history')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while getting game history'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const getUserGameHistory = async (userId) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_BASE}/users/${userId}/game-history`, {
        method: 'GET',
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        return { success: true, histories: data.histories }
      } else {
        setError(data.error || 'Failed to get user game history')
        return { success: false, error: data.error }
      }
    } catch (error) {
      const errorMsg = 'Network error while getting user game history'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const clearError = () => {
    setError('')
  }

  return {
    loading,
    error,
    clearError,
    saveGameState,
    loadGameState,
    getGameStates,
    createAutoSave,
    getGameActions,
    undoAction,
    finishGame,
    getGameHistory,
    getUserGameHistory
  }
}

