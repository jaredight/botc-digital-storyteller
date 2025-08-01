import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useGame } from '../hooks/useGame'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Crown, 
  Users, 
  Clock, 
  Vote, 
  Skull, 
  Eye, 
  EyeOff, 
  MessageSquare,
  Settings,
  Loader2,
  Moon,
  Sun
} from 'lucide-react'

export default function GameBoard() {
  const { gameId } = useParams()
  const { user } = useAuth()
  const { currentGame, getGame, submitVote, nominatePlayer } = useGame()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [showRoles, setShowRoles] = useState(false)

  useEffect(() => {
    loadGame()
  }, [gameId])

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

  const handlePlayerClick = (player) => {
    setSelectedPlayer(player)
  }

  const handleVote = async (targetId) => {
    try {
      const result = await submitVote(parseInt(gameId), targetId)
      if (result.success) {
        await loadGame() // Refresh game state
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to submit vote')
    }
  }

  const handleNominate = async (targetId) => {
    try {
      const result = await nominatePlayer(parseInt(gameId), targetId)
      if (result.success) {
        await loadGame() // Refresh game state
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to nominate player')
    }
  }

  const getUserInitials = (username) => {
    return username ? username.slice(0, 2).toUpperCase() : 'U'
  }

  const getPlayerColor = (player) => {
    if (!player.is_alive) return 'bg-gray-500'
    if (showRoles && player.team) {
      switch (player.team) {
        case 'townsfolk': return 'bg-blue-500'
        case 'outsider': return 'bg-cyan-500'
        case 'minion': return 'bg-red-500'
        case 'demon': return 'bg-purple-500'
        default: return 'bg-gray-500'
      }
    }
    return 'bg-gradient-to-br from-blue-500 to-purple-600'
  }

  const currentPlayer = currentGame?.players?.find(p => p.user_id === user?.id)
  const isHost = currentGame && user && currentGame.host_id === user.id

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
                {currentGame.phase === 'night' ? (
                  <Moon className="mr-2 h-6 w-6" />
                ) : (
                  <Sun className="mr-2 h-6 w-6" />
                )}
                {currentGame.phase === 'night' ? 'Night Phase' : 'Day Phase'}
              </CardTitle>
              <CardDescription className="text-slate-300">
                {currentGame.script?.name} - Day {currentGame.day_number || 1}
              </CardDescription>
            </div>
            <div className="flex items-center space-x-4">
              {isHost && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRoles(!showRoles)}
                  className="border-slate-600 hover:bg-slate-700"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  {showRoles ? 'Hide Roles' : 'Show Roles'}
                </Button>
              )}
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {currentGame.status}
              </Badge>
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

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Game Board - Player Circle */}
        <div className="lg:col-span-3">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Users className="mr-2 h-5 w-5" />
                Town Square
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative w-full h-96 flex items-center justify-center">
                {/* Player Circle */}
                <div className="relative w-80 h-80 rounded-full border-2 border-slate-600">
                  {currentGame.players?.map((player, index) => {
                    const angle = (index / currentGame.players.length) * 2 * Math.PI - Math.PI / 2
                    const x = Math.cos(angle) * 140 + 160
                    const y = Math.sin(angle) * 140 + 160
                    
                    return (
                      <div
                        key={player.id}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                        style={{ left: x, top: y }}
                        onClick={() => handlePlayerClick(player)}
                      >
                        <div className="text-center">
                          <Avatar className={`h-12 w-12 border-2 ${
                            selectedPlayer?.id === player.id ? 'border-yellow-400' : 'border-slate-600'
                          } ${!player.is_alive ? 'opacity-50' : ''}`}>
                            <AvatarFallback className={getPlayerColor(player)}>
                              {getUserInitials(player.username)}
                            </AvatarFallback>
                          </Avatar>
                          <div className="mt-1 text-xs text-white font-medium">
                            {player.username}
                          </div>
                          {!player.is_alive && (
                            <Skull className="h-4 w-4 text-red-400 mx-auto mt-1" />
                          )}
                          {showRoles && player.role_name && (
                            <div className="text-xs text-slate-300 mt-1">
                              {player.role_name}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Game Controls */}
        <div className="space-y-6">
          {/* Player Info */}
          {currentPlayer && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Your Role</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {currentPlayer.role_name || 'Unknown'}
                  </div>
                  {currentPlayer.role && (
                    <div className="text-sm text-slate-300 mt-2">
                      {currentPlayer.role.ability}
                    </div>
                  )}
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Team:</span>
                  <span className="text-white capitalize">{currentPlayer.team}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Status:</span>
                  <span className={`${currentPlayer.is_alive ? 'text-green-400' : 'text-red-400'}`}>
                    {currentPlayer.is_alive ? 'Alive' : 'Dead'}
                  </span>
                </div>
                {!currentPlayer.is_alive && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Ghost Votes:</span>
                    <span className="text-white">{currentPlayer.ghost_votes || 0}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          {selectedPlayer && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Actions</CardTitle>
                <CardDescription className="text-slate-300">
                  Selected: {selectedPlayer.username}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {currentGame.phase === 'day' && currentPlayer?.can_vote && (
                  <Button
                    onClick={() => handleVote(selectedPlayer.id)}
                    className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
                    disabled={selectedPlayer.id === currentPlayer.id}
                  >
                    <Vote className="mr-2 h-4 w-4" />
                    Vote to Execute
                  </Button>
                )}
                
                {currentGame.phase === 'day' && currentPlayer?.is_alive && (
                  <Button
                    onClick={() => handleNominate(selectedPlayer.id)}
                    variant="outline"
                    className="w-full border-slate-600 hover:bg-slate-700"
                    disabled={selectedPlayer.id === currentPlayer.id}
                  >
                    Nominate for Execution
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Game Status */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Game Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Phase:</span>
                <span className="text-white capitalize">{currentGame.phase}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Day:</span>
                <span className="text-white">{currentGame.day_number || 1}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Alive:</span>
                <span className="text-white">
                  {currentGame.players?.filter(p => p.is_alive).length || 0}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Dead:</span>
                <span className="text-white">
                  {currentGame.players?.filter(p => !p.is_alive).length || 0}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Chat/Notes */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <MessageSquare className="mr-2 h-5 w-5" />
                Notes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-slate-300">
                Game chat and notes will be implemented in the next phase.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

