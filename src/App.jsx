import React, { useEffect, useState } from 'react'
import Chatbot from './components/Chatbot'
import SignUp from './components/SignUp'
import Login from './components/Login'
import { tokenManager } from './services/api'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('loading')

  useEffect(() => {
    const updateRoute = () => {
      const path = window.location.pathname
      const isLoggedIn = tokenManager.isLoggedIn()

      // Jika path adalah /login atau /signup, tampilkan halaman tersebut
      if (path === '/login' || path === '/login/') {
        setCurrentPage('login')
      } else if (path === '/signup' || path === '/signup/') {
        setCurrentPage('signup')
      } else {
        // Untuk path lain (/) - check apakah sudah login
        if (isLoggedIn) {
          setCurrentPage('chatbot')
        } else {
          // Belum login, redirect ke /login
          window.history.pushState({}, '', '/login')
          setCurrentPage('login')
        }
      }
    }

    // Update route saat component mount
    updateRoute()

    // Handle link clicks
    const handleLinkClick = (e) => {
      const target = e.target.closest('a')
      if (target && target.href.includes(window.location.origin)) {
        const href = target.getAttribute('href')
        if (href && href.startsWith('/')) {
          e.preventDefault()
          window.history.pushState({}, '', href)
          updateRoute()
        }
      }
    }

    // Handle browser back/forward buttons
    const handlePopState = () => {
      updateRoute()
    }

    document.addEventListener('click', handleLinkClick)
    window.addEventListener('popstate', handlePopState)

    return () => {
      document.removeEventListener('click', handleLinkClick)
      window.removeEventListener('popstate', handlePopState)
    }
  }, [])

  if (currentPage === 'loading') {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '18px', color: '#666' }}>Loading...</div>
  }

  return (
    <div className="App">
      {currentPage === 'chatbot' && <Chatbot />}
      {currentPage === 'signup' && <SignUp />}
      {currentPage === 'login' && <Login />}
    </div>
  )
}

export default App
