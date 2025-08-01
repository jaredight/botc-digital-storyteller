import { useAuth } from '../hooks/useAuth'
import { useGame } from '../hooks/useGame'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator 
} from '@/components/ui/dropdown-menu'
import { Crown, LogOut, Settings, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const { user, logout } = useAuth()
  const { currentGame, leaveGame } = useGame()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleLeaveGame = async () => {
    if (currentGame) {
      await leaveGame(currentGame.id)
      navigate('/')
    }
  }

  const getUserInitials = (username) => {
    return username ? username.slice(0, 2).toUpperCase() : 'U'
  }

  return (
    <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo and Title */}
        <div 
          className="flex items-center space-x-3 cursor-pointer"
          onClick={() => navigate('/')}
        >
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Crown className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Blood on the Clocktower</h1>
            <p className="text-sm text-slate-300">Digital Storyteller</p>
          </div>
        </div>

        {/* Game Info */}
        {currentGame && (
          <div className="hidden md:flex items-center space-x-4 text-white">
            <div className="text-center">
              <p className="text-sm text-slate-300">Game Code</p>
              <p className="font-mono font-bold text-lg">{currentGame.join_code}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-slate-300">Players</p>
              <p className="font-bold">{currentGame.player_count}/{currentGame.settings?.max_players || 15}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-slate-300">Status</p>
              <p className="font-bold capitalize">{currentGame.status}</p>
            </div>
          </div>
        )}

        {/* User Menu */}
        {user && (
          <div className="flex items-center space-x-4">
            {currentGame && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleLeaveGame}
                className="text-white border-slate-600 hover:bg-slate-700"
              >
                Leave Game
              </Button>
            )}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                      {getUserInitials(user.username)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <div className="flex flex-col space-y-1 p-2">
                  <p className="text-sm font-medium leading-none">{user.username}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/profile')}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>
    </header>
  )
}

