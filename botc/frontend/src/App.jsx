import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import { GameProvider } from './hooks/useGame'
import { SocketProvider } from './hooks/useSocket'
import { Toaster } from '@/components/ui/toaster'
import Header from './components/Header'
import LoginPage from './components/LoginPage'
import HomePage from './components/HomePage'
import GameLobby from './components/GameLobby'
import GameBoard from './components/GameBoard'
import './App.css'

function AppContent() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route 
            path="/login" 
            element={user ? <Navigate to="/" /> : <LoginPage />} 
          />
          <Route 
            path="/" 
            element={user ? <HomePage /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/game/:gameId/lobby" 
            element={user ? <GameLobby /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/game/:gameId" 
            element={user ? <GameBoard /> : <Navigate to="/login" />} 
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Toaster />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <SocketProvider>
          <GameProvider>
            <AppContent />
          </GameProvider>
        </SocketProvider>
      </AuthProvider>
    </Router>
  )
}

export default App