import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useGame } from '../hooks/useGame'
import { useSocket } from '../hooks/useSocket'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Crown, Users, Play, UserCheck, UserX, Copy, Check, Loader2, Wifi, WifiOff } from 'lucide-react'
import GameChat from './GameChat'

export default function GameLobby() {
  const { gameId } = useParams()
  const { user } = useAuth()
  const { currentGame, getGame, toggleReady, startGame, leaveGame } = useGame()
  const { connected, joinGame, leaveGame: socketLeaveGame, gameUpdates, sendGameUpdate } = useSocket()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copiedCode, setCopiedCode] = useState(false)

  useEffect(() => {
    loadGame()
  }, [gameId])

  useEffect(() => {
    // Join the game room for real-time updates
    if (gameId && connected) {
      joinGame(parseInt(gameId))
    }

    return () => {
      // Leave the game room when component unmounts
      if (gameId && connected) {
        socketLeaveGame(parseInt(gameId))
      }
    }
  }, [gameId, connected])

  useEffect(() => {
    // Listen for real-time game updates
    const latestUpdate = gameUpdates[gameUpdates.length - 1]
    if (latestUpdate && latestUpdate.type === 'player_joined' || 
        latestUpdate?.type === 'player_left' || 
        latestUpdate?.type === 'player_ready_changed' ||
        latestUpdate?.type === 'game_started') {
      // Refresh game state when players join/leave or ready status changes
      loadGame()
    }
  }, [gameUpdates])

  const loadGame = async () => {
    setLoading(true)
    try {
      const result = await getGame(parseInt(gameId))
      if (!result.success) {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to load game')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleReady = async () => {
    try {
      const result = await toggleReady(parseInt(gameId))
      if (result.success) {
        // Send real-time update to other players
        sendGameUpdate(parseInt(gameId), 'player_ready_changed', {
          player_id: user.id,
          is_ready: result.isReady
        })
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to update ready status')
    }
  }

  const handleStartGame = async () => {
    try {
      const result = await startGame(parseInt(gameId))
      if (result.success) {
        // Send real-time update to all players
        sendGameUpdate(parseInt(gameId), 'game_started', {
          game: result.game
        })
        navigate(`/game/${gameId}`)
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to start game')
    }
  }

  const handleLeaveGame = async () => {
    try {
      await leaveGame(parseInt(gameId))
      // Send real-time update to other players
      sendGameUpdate(parseInt(gameId), 'player_left', {
        player_id: user.id,
        username: user.username
      })
      navigate('/')
    } catch (error) {
      setError('Failed to leave game')
    }
  }

  const copyJoinCode = async () => {
    try {
      await navigator.clipboard.writeText(currentGame.join_code)
      setCopiedCode(true)
      setTimeout(() => setCopiedCode(false), 2000)
    } catch (error) {
      console.error('Failed to copy join code:', error)
    }
  }

  const getUserInitials = (username) => {
    return username ? username.slice(0, 2).toUpperCase() : 'U'
  }

  const isHost = currentGame && user && currentGame.host_id === user.id
  const currentPlayer = currentGame?.players?.find(p => p.user_id === user?.id)
  const canStart = currentGame?.player_count >= 5 && currentGame?.players?.every(p => p.is_ready)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="h-8 w-8 animate-spin text-white" />
        <span className="ml-2 text-white">Loading game...</span>
      </div>
    )
  }

  if (!currentGame) {
    return (
      <div className="text-center">
        <Alert variant="destructive">
          <AlertDescription>Game not found or you don't have access to it.</AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/')} className="mt-4">
          Return Home
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Game Header */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white text-2xl flex items-center">
                Game Lobby
                {connected ? (
                  <Wifi className="ml-2 h-5 w-5 text-green-400" />
                ) : (
                  <WifiOff className="ml-2 h-5 w-5 text-red-400" />
                )}
              </CardTitle>
              <CardDescription className="text-slate-300">
                Waiting for players to join and get ready
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-slate-300">Join Code:</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyJoinCode}
                  className="font-mono text-lg border-slate-600 hover:bg-slate-700"
                >
                  {currentGame.join_code}
                  {copiedCode ? (
                    <Check className="ml-2 h-4 w-4 text-green-400" />
                  ) : (
                    <Copy className="ml-2 h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="text-sm text-slate-400">
                Share this code with other players
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Players List */}
        <div className="lg:col-span-2">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Users className="mr-2 h-5 w-5" />
                Players ({currentGame.player_count}/{currentGame.settings?.max_players || 15})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {currentGame.players?.map((player) => (
                  <div
                    key={player.id}
                    className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg"
                  >
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                        {getUserInitials(player.username)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-white font-medium">{player.username}</span>
                        {player.user_id === currentGame.host_id && (
                          <Crown className="h-4 w-4 text-yellow-400" />
                        )}
                      </div>
                      <div className="flex items-center space-x-2 mt-1">
                        {player.is_ready ? (
                          <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                            <UserCheck className="mr-1 h-3 w-3" />
                            Ready
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-slate-600 text-slate-400">
                            <UserX className="mr-1 h-3 w-3" />
                            Not Ready
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Chat Section */}
          <div className="mt-6">
            <GameChat gameId={parseInt(gameId)} />
          </div>
        </div>

        {/* Game Info & Controls */}
        <div className="space-y-6">
          {/* Game Settings */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Game Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">Script:</span>
                <span className="text-white">{currentGame.script?.name || 'None'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Max Players:</span>
                <span className="text-white">{currentGame.settings?.max_players || 15}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Discussion Time:</span>
                <span className="text-white">{Math.floor((currentGame.settings?.discussion_time || 600) / 60)} min</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Voting Time:</span>
                <span className="text-white">{Math.floor((currentGame.settings?.voting_time || 120) / 60)} min</span>
              </div>
            </CardContent>
          </Card>

          {/* Player Controls */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Ready Toggle */}
              <Button
                onClick={handleToggleReady}
                variant={currentPlayer?.is_ready ? "secondary" : "default"}
                className="w-full"
                disabled={!connected}
              >
                {currentPlayer?.is_ready ? (
                  <>
                    <UserX className="mr-2 h-4 w-4" />
                    Mark Not Ready
                  </>
                ) : (
                  <>
                    <UserCheck className="mr-2 h-4 w-4" />
                    Mark Ready
                  </>
                )}
              </Button>

              {/* Start Game (Host Only) */}
              {isHost && (
                <Button
                  onClick={handleStartGame}
                  disabled={!canStart || !connected}
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
                >
                  <Play className="mr-2 h-4 w-4" />
                  Start Game
                </Button>
              )}

              {/* Leave Game */}
              <Button
                onClick={handleLeaveGame}
                variant="destructive"
                className="w-full"
              >
                Leave Game
              </Button>
            </CardContent>
          </Card>

          {/* Game Status */}
          {!canStart && (
            <Alert>
              <AlertDescription className="text-sm">
                {currentGame.player_count < 5 
                  ? `Need at least ${5 - currentGame.player_count} more players to start`
                  : 'Waiting for all players to be ready'
                }
              </AlertDescription>
            </Alert>
          )}

          {/* Connection Status */}
          {!connected && (
            <Alert variant="destructive">
              <WifiOff className="h-4 w-4" />
              <AlertDescription>
                Connection lost. Real-time updates disabled.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  )
}

