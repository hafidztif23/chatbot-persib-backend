import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// Component Rekan Kamu
import Chatbot from './components/Chatbot'
import SignUp from './components/SignUp'
import Login from './components/Login'
import { tokenManager } from './services/api'

// Component Lokal Kamu
import LandingPage from './pages/LandingPage'
import Profile from './pages/Profile'
import Settings from './pages/Settings'

import './App.css'

function App() {
  // Cek status login
  const isLoggedIn = tokenManager.isLoggedIn()

  // PERHATIKAN: Kita langsung me-return <BrowserRouter> di sini
  return (
    <BrowserRouter>
      <Routes>
        {/* Rute Utama & Lokal */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/profile" element={isLoggedIn ? <Profile /> : <Navigate to="/login" replace />} />
        <Route path="/settings" element={isLoggedIn ? <Settings /> : <Navigate to="/login" replace />} />

        {/* Rute Auth (Login/Signup) */}
        <Route path="/login" element={!isLoggedIn ? <Login /> : <Navigate to="/chat" replace />} />
        <Route path="/signup" element={!isLoggedIn ? <SignUp /> : <Navigate to="/chat" replace />} />

        {/* Rute Chatbot */}
        <Route path="/chat" element={isLoggedIn ? <Chatbot /> : <Navigate to="/login" replace />} />

        {/* Rute Sapu Jagat jika URL ngawur */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App