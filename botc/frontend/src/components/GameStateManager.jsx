import { useState, useEffect } from 'react'
import { useGameState } from '../hooks/useGameState'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Save, 
  FolderOpen, 
  History, 
  Undo, 
  Clock, 
  User, 
  Calendar,
  Download,
  Upload,
  Trash2,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'

export default function GameStateManager({ gameId, isHost, isVisible = true }) {
  const { user } = useAuth()
  const {
    loading,
    error,
    clearError,
    saveGameState,
    loadGameState,
    getGameStates,
    createAutoSave,
    getGameActions,
    undoAction
  } = useGameState()

  const [states, setStates] = useState([])
  const [actions, setActions] = useState([])
  const [newStateName, setNewStateName] = useState('')
  const [selectedState, setSelectedState] = useState(null)
  const [undoReason, setUndoReason] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showLoadDialog, setShowLoadDialog] = useState(false)
  const [showUndoDialog, setShowUndoDialog] = useState(false)
  const [selectedAction, setSelectedAction] = useState(null)

  useEffect(() => {
    if (isVisible && gameId) {
      loadStatesAndActions()
    }
  }, [isVisible, gameId])

  const loadStatesAndActions = async () => {
    if (isHost) {
      // Load saved states
      const statesResult = await getGameStates(gameId)
      if (statesResult.success) {
        setStates(statesResult.states)
      }
    }

    // Load recent actions
    const actionsResult = await getGameActions(gameId, 20)
    if (actionsResult.success) {
      setActions(actionsResult.actions)
    }
  }

  const handleSaveState = async () => {
    if (!newStateName.trim()) return

    const result = await saveGameState(gameId, newStateName.trim())
    if (result.success) {
      setNewStateName('')
      setShowSaveDialog(false)
      await loadStatesAndActions()
    }
  }

  const handleLoadState = async (stateId) => {
    const result = await loadGameState(gameId, stateId)
    if (result.success) {
      setShowLoadDialog(false)
      setSelectedState(null)
      await loadStatesAndActions()
      // Refresh the game state in parent component
      window.location.reload() // Simple refresh for now
    }
  }

  const handleCreateAutoSave = async () => {
    const result = await createAutoSave(gameId)
    if (result.success) {
      await loadStatesAndActions()
    }
  }

  const handleUndoAction = async (actionId) => {
    const result = await undoAction(gameId, actionId, undoReason)
    if (result.success) {
      setShowUndoDialog(false)
      setSelectedAction(null)
      setUndoReason('')
      await loadStatesAndActions()
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'vote': return '🗳️'
      case 'nominate': return '👆'
      case 'execute': return '💀'
      case 'save_state': return '💾'
      case 'load_state': return '📁'
      case 'undo_action': return '↩️'
      case 'finish_game': return '🏁'
      default: return '📝'
    }
  }

  const getActionColor = (actionType) => {
    switch (actionType) {
      case 'execute': return 'text-red-400'
      case 'save_state': return 'text-green-400'
      case 'load_state': return 'text-blue-400'
      case 'undo_action': return 'text-yellow-400'
      case 'finish_game': return 'text-purple-400'
      default: return 'text-slate-400'
    }
  }

  if (!isVisible) return null

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <History className="mr-2 h-5 w-5" />
          Game State Manager
        </CardTitle>
        <CardDescription className="text-slate-300">
          {isHost ? 'Save, load, and manage game states' : 'View game history and actions'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
            <Button variant="ghost" size="sm" onClick={clearError} className="ml-auto">
              <XCircle className="h-4 w-4" />
            </Button>
          </Alert>
        )}

        <Tabs defaultValue="actions" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-700">
            <TabsTrigger value="actions" className="text-slate-300">Actions</TabsTrigger>
            {isHost && <TabsTrigger value="saves" className="text-slate-300">Saves</TabsTrigger>}
            {isHost && <TabsTrigger value="controls" className="text-slate-300">Controls</TabsTrigger>}
          </TabsList>

          {/* Recent Actions Tab */}
          <TabsContent value="actions" className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-white font-medium">Recent Actions</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={loadStatesAndActions}
                disabled={loading}
                className="border-slate-600 hover:bg-slate-700"
              >
                <History className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>

            <ScrollArea className="h-64">
              <div className="space-y-2">
                {actions.length === 0 ? (
                  <div className="text-center text-slate-400 py-8">
                    <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No actions recorded yet</p>
                  </div>
                ) : (
                  actions.map((action) => (
                    <div
                      key={action.id}
                      className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-lg">{getActionIcon(action.action_type)}</span>
                        <div>
                          <div className={`font-medium ${getActionColor(action.action_type)}`}>
                            {action.action_type.replace('_', ' ').toUpperCase()}
                          </div>
                          <div className="text-xs text-slate-400">
                            <Clock className="inline h-3 w-3 mr-1" />
                            {formatDate(action.performed_at)}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {action.is_undone && (
                          <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                            Undone
                          </Badge>
                        )}
                        
                        {isHost && !action.is_undone && action.action_type !== 'undo_action' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedAction(action)
                              setShowUndoDialog(true)
                            }}
                            className="text-yellow-400 hover:bg-yellow-400/10"
                          >
                            <Undo className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Saved States Tab (Host Only) */}
          {isHost && (
            <TabsContent value="saves" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-medium">Saved States</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSaveDialog(true)}
                  disabled={loading}
                  className="border-slate-600 hover:bg-slate-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save State
                </Button>
              </div>

              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {states.length === 0 ? (
                    <div className="text-center text-slate-400 py-8">
                      <Save className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No saved states yet</p>
                    </div>
                  ) : (
                    states.map((state) => (
                      <div
                        key={state.id}
                        className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                      >
                        <div>
                          <div className="text-white font-medium">{state.state_name}</div>
                          <div className="text-xs text-slate-400">
                            <Calendar className="inline h-3 w-3 mr-1" />
                            {formatDate(state.created_at)}
                          </div>
                          <div className="text-xs text-slate-400 mt-1">
                            {state.state_preview.player_count} players, Day {state.state_preview.day}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {state.is_auto_save && (
                            <Badge variant="outline" className="text-blue-400 border-blue-400">
                              Auto
                            </Badge>
                          )}
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedState(state)
                              setShowLoadDialog(true)
                            }}
                            className="text-blue-400 hover:bg-blue-400/10"
                          >
                            <FolderOpen className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          )}

          {/* Controls Tab (Host Only) */}
          {isHost && (
            <TabsContent value="controls" className="space-y-4">
              <div className="grid grid-cols-1 gap-3">
                <Button
                  onClick={handleCreateAutoSave}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Create Auto-Save
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => setShowSaveDialog(true)}
                  disabled={loading}
                  className="w-full border-slate-600 hover:bg-slate-700"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Manual Save
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => setShowLoadDialog(true)}
                  disabled={loading || states.length === 0}
                  className="w-full border-slate-600 hover:bg-slate-700"
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Load State
                </Button>
              </div>
            </TabsContent>
          )}
        </Tabs>

        {/* Save State Dialog */}
        <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
          <DialogContent className="bg-slate-800 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Save Game State</DialogTitle>
              <DialogDescription className="text-slate-300">
                Enter a name for this save state
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <Input
                value={newStateName}
                onChange={(e) => setNewStateName(e.target.value)}
                placeholder="Save state name..."
                className="bg-slate-700 border-slate-600 text-white"
                maxLength={100}
              />
              
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setShowSaveDialog(false)}
                  className="border-slate-600 hover:bg-slate-700"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveState}
                  disabled={!newStateName.trim() || loading}
                  className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Save
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Load State Dialog */}
        <Dialog open={showLoadDialog} onOpenChange={setShowLoadDialog}>
          <DialogContent className="bg-slate-800 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Load Game State</DialogTitle>
              <DialogDescription className="text-slate-300">
                Select a saved state to load. This will overwrite the current game state.
              </DialogDescription>
            </DialogHeader>
            
            <ScrollArea className="max-h-64">
              <div className="space-y-2">
                {states.map((state) => (
                  <div
                    key={state.id}
                    className={`p-3 rounded-lg cursor-pointer border-2 transition-colors ${
                      selectedState?.id === state.id
                        ? 'border-blue-400 bg-blue-400/10'
                        : 'border-slate-600 bg-slate-700/50 hover:bg-slate-700'
                    }`}
                    onClick={() => setSelectedState(state)}
                  >
                    <div className="text-white font-medium">{state.state_name}</div>
                    <div className="text-xs text-slate-400">
                      {formatDate(state.created_at)} • Day {state.state_preview.day}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowLoadDialog(false)}
                className="border-slate-600 hover:bg-slate-700"
              >
                Cancel
              </Button>
              <Button
                onClick={() => handleLoadState(selectedState.id)}
                disabled={!selectedState || loading}
                className="bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
              >
                <FolderOpen className="mr-2 h-4 w-4" />
                Load
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Undo Action Dialog */}
        <Dialog open={showUndoDialog} onOpenChange={setShowUndoDialog}>
          <DialogContent className="bg-slate-800 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Undo Action</DialogTitle>
              <DialogDescription className="text-slate-300">
                Are you sure you want to undo this action? This cannot be reversed.
              </DialogDescription>
            </DialogHeader>
            
            {selectedAction && (
              <div className="p-3 bg-slate-700/50 rounded-lg">
                <div className="text-white font-medium">
                  {selectedAction.action_type.replace('_', ' ').toUpperCase()}
                </div>
                <div className="text-xs text-slate-400">
                  {formatDate(selectedAction.performed_at)}
                </div>
              </div>
            )}
            
            <Input
              value={undoReason}
              onChange={(e) => setUndoReason(e.target.value)}
              placeholder="Reason for undo (optional)..."
              className="bg-slate-700 border-slate-600 text-white"
              maxLength={200}
            />
            
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowUndoDialog(false)}
                className="border-slate-600 hover:bg-slate-700"
              >
                Cancel
              </Button>
              <Button
                onClick={() => handleUndoAction(selectedAction.id)}
                disabled={loading}
                variant="destructive"
              >
                <Undo className="mr-2 h-4 w-4" />
                Undo
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}

