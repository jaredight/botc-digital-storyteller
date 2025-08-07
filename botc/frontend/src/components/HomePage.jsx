import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useGame } from '../hooks/useGame'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Plus, Users, Crown, BookOpen, Loader2, Copy, Check } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function HomePage() {
  const { user } = useAuth()
  const { createGame, joinGame, scripts, loading } = useGame()
  const navigate = useNavigate()
  
  const [joinCode, setJoinCode] = useState('')
  const [selectedScript, setSelectedScript] = useState('')
  const [gameSettings, setGameSettings] = useState({
    max_players: 15,
    discussion_time: 600,
    voting_time: 120
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [isJoining, setIsJoining] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [copiedCode, setCopiedCode] = useState(false)

  useEffect(() => {
    if (scripts.length > 0 && !selectedScript) {
      // Default to Trouble Brewing script
      const troubleBrewing = scripts.find(s => s.name === 'Trouble Brewing')
      if (troubleBrewing) {
        setSelectedScript(troubleBrewing.id.toString())
      }
    }
  }, [scripts, selectedScript])

  const handleCreateGame = async () => {
    if (!selectedScript) {
      setError('Please select a script')
      return
    }

    setError('')
    setIsCreating(true)

    try {
      const result = await createGame(parseInt(selectedScript), gameSettings)
      
      if (result.success) {
        setSuccess(`Game created! Join code: ${result.game.join_code}`)
        setShowCreateDialog(false)
        navigate(`/game/${result.game.id}/lobby`)
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to create game')
    } finally {
      setIsCreating(false)
    }
  }

  const handleJoinGame = async () => {
    if (!joinCode.trim()) {
      setError('Please enter a join code')
      return
    }

    setError('')
    setIsJoining(true)

    try {
      const result = await joinGame(joinCode.trim().toUpperCase())
      
      if (result.success) {
        setSuccess('Joined game successfully!')
        navigate(`/game/${result.game.id}/lobby`)
      } else {
        setError(result.error)
      }
    } catch (error) {
      setError('Failed to join game')
    } finally {
      setIsJoining(false)
    }
  }

  const copyJoinCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code)
      setCopiedCode(true)
      setTimeout(() => setCopiedCode(false), 2000)
    } catch (error) {
      console.error('Failed to copy join code:', error)
    }
  }

  const getSelectedScriptInfo = () => {
    if (!selectedScript) return null
    return scripts.find(s => s.id === parseInt(selectedScript))
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-xl text-slate-300 mb-8">
          Ready to play Blood on the Clocktower? Create a new game or join an existing one.
        </p>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {success && (
        <Alert className="border-green-500 bg-green-500/10 text-green-400">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Main Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Create Game */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Crown className="mr-2 h-5 w-5" />
              Host a Game
            </CardTitle>
            <CardDescription className="text-slate-300">
              Create a new game and invite players to join
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="w-full bg-gradient-to-r from-red-500 to-purple-600 hover:from-red-600 hover:to-purple-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Game
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Game</DialogTitle>
                  <DialogDescription className="text-slate-300">
                    Configure your game settings and choose a script
                  </DialogDescription>
                </DialogHeader>
                
                <div className="space-y-6">
                  {/* Script Selection */}
                  <div className="space-y-2">
                    <Label className="text-white">Script</Label>
                    <Select value={selectedScript} onValueChange={setSelectedScript}>
                      <SelectTrigger className="bg-slate-700 border-slate-600">
                        <SelectValue placeholder="Choose a script" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        {scripts.map((script) => (
                          <SelectItem key={script.id} value={script.id.toString()}>
                            <div className="flex items-center space-x-2">
                              <span>{script.name}</span>
                              {script.is_official && (
                                <Badge variant="secondary" className="text-xs">Official</Badge>
                              )}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    
                    {/* Script Info */}
                    {getSelectedScriptInfo() && (
                      <div className="p-3 bg-slate-700/50 rounded-lg">
                        <p className="text-sm text-slate-300 mb-2">
                          {getSelectedScriptInfo().description}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-slate-400">
                          <span>Players: {getSelectedScriptInfo().player_count_min}-{getSelectedScriptInfo().player_count_max}</span>
                          <span>Roles: {getSelectedScriptInfo().role_count}</span>
                          <span>Author: {getSelectedScriptInfo().author}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  <Separator className="bg-slate-600" />

                  {/* Game Settings */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label className="text-white">Max Players</Label>
                      <Select 
                        value={gameSettings.max_players.toString()} 
                        onValueChange={(value) => setGameSettings({...gameSettings, max_players: parseInt(value)})}
                      >
                        <SelectTrigger className="bg-slate-700 border-slate-600">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          {Array.from({length: 11}, (_, i) => i + 5).map(num => (
                            <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-white">Discussion Time (min)</Label>
                      <Select 
                        value={(gameSettings.discussion_time / 60).toString()} 
                        onValueChange={(value) => setGameSettings({...gameSettings, discussion_time: parseInt(value) * 60})}
                      >
                        <SelectTrigger className="bg-slate-700 border-slate-600">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          <SelectItem value="5">5 min</SelectItem>
                          <SelectItem value="10">10 min</SelectItem>
                          <SelectItem value="15">15 min</SelectItem>
                          <SelectItem value="20">20 min</SelectItem>
                          <SelectItem value="30">30 min</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-white">Voting Time (min)</Label>
                      <Select 
                        value={(gameSettings.voting_time / 60).toString()} 
                        onValueChange={(value) => setGameSettings({...gameSettings, voting_time: parseInt(value) * 60})}
                      >
                        <SelectTrigger className="bg-slate-700 border-slate-600">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          <SelectItem value="1">1 min</SelectItem>
                          <SelectItem value="2">2 min</SelectItem>
                          <SelectItem value="3">3 min</SelectItem>
                          <SelectItem value="5">5 min</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button 
                    onClick={handleCreateGame} 
                    className="w-full bg-gradient-to-r from-red-500 to-purple-600 hover:from-red-600 hover:to-purple-700"
                    disabled={isCreating}
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Game...
                      </>
                    ) : (
                      <>
                        <Crown className="mr-2 h-4 w-4" />
                        Create Game
                      </>
                    )}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>

        {/* Join Game */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Users className="mr-2 h-5 w-5" />
              Join a Game
            </CardTitle>
            <CardDescription className="text-slate-300">
              Enter a join code to join an existing game
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="join-code" className="text-white">Game Join Code</Label>
              <Input
                id="join-code"
                type="text"
                placeholder="Enter 6-character code"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                maxLength={6}
                className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 font-mono text-center text-lg"
              />
            </div>
            
            <Button 
              onClick={handleJoinGame} 
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
              disabled={isJoining}
            >
              {isJoining ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Joining Game...
                </>
              ) : (
                <>
                  <Users className="mr-2 h-4 w-4" />
                  Join Game
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Scripts Section */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <BookOpen className="mr-2 h-5 w-5" />
            Available Scripts
          </CardTitle>
          <CardDescription className="text-slate-300">
            Browse and learn about different Blood on the Clocktower scripts
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-white" />
              <span className="ml-2 text-white">Loading scripts...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scripts.map((script) => (
                <Card key={script.id} className="bg-slate-700/50 border-slate-600">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-white text-lg">{script.name}</CardTitle>
                      {script.is_official && (
                        <Badge variant="secondary" className="text-xs">Official</Badge>
                      )}
                    </div>
                    <CardDescription className="text-slate-300 text-sm">
                      {script.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{script.player_count_min}-{script.player_count_max} players</span>
                      <span>{script.role_count} roles</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      by {script.author}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

