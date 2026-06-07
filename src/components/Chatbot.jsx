import React, { useState, useEffect } from 'react'
import './Chatbot.css'
import PersibLogo from '../image/Logo_Persib_Bandung.png'
import { chatAPI, tokenManager } from '../services/api'
import { useAuth } from '../hooks/useAuth'

function Chatbot() {
  const { logout } = useAuth()
  const [user, setUser] = useState(tokenManager.getUser())
  const [isNewChat, setIsNewChat] = useState(true)
  const [inputMessage, setInputMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)


  const suggestedQuestions = [
    'Silapa top skorer Persib musim ini?',
    'Analisis formasi 3-4-3 Coach Bojan',
    'Kapan jadwal Persib vs Persija?',
    'Tips bertahan ala Robby Darwin'
  ]

  const handleSuggestedQuestion = (question) => {
    handleSendMessage(null, question)
  }

  const handleSendMessage = async (e, messageText = null) => {
    if (e) e.preventDefault()
    
    const textToSend = messageText || inputMessage
    if (textToSend.trim() === '') return

    setIsNewChat(false)

    // Tambah pesan user
    const newUserMessage = {
      id: messages.length + 1,
      text: textToSend,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, newUserMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Kirim ke API
      const response = await chatAPI.sendMessage(textToSend)
      
      // Tambah respons bot
      const botResponse = {
        id: messages.length + 2,
        text: response.response || response.answer || 'Maaf, saya tidak dapat memproses pertanyaan Anda.',
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prevMessages => [...prevMessages, botResponse])
    } catch (error) {
      console.error('Chat error:', error)
      
      // Tambah error message
      const errorMessage = {
        id: messages.length + 2,
        text: `Maaf, terjadi kesalahan: ${error.message}`,
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prevMessages => [...prevMessages, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="chatbot-main">
      {/* Sidebar */}
      <aside className="chatbot-sidebar">
        <div className="sidebar-header">
          <div className="bot-icon">🤖</div>
          <div className="bot-title">
            <h3>MAUNG BOT</h3>
            <p>Powered by AI</p>
          </div>
        </div>

        <button className="new-chat-btn" onClick={() => {
          setIsNewChat(true)
          setMessages([])
          setInputMessage('')
        }}>
          ➕ Obrolan Baru
        </button>

        <div className="sidebar-menu">
          <h4>MENU UTAMA</h4>
          <div className="menu-item active">💬 Chat Sekarang</div>
        </div>

        <div className="sidebar-footer">
          <h4>USER</h4>
          {user && (
            <div className="user-info" style={{ padding: '10px', fontSize: '12px', marginBottom: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
              <p><strong>{user.nama_lengkap}</strong></p>
              <p>{user.email}</p>
              <p>Member: {user.membership}</p>
            </div>
          )}
          <h4>PENGATURAN</h4>
          <div className="settings-item">
            <span>🎵 Tone</span>
          </div>
          <div className="settings-item">
            <span>🌐 Language</span>
          </div>
        </div>

        <button className="logout-btn" onClick={handleLogout}>Keluar</button>
      </aside>

      {/* Main Chat Area */}
      <main className="chatbot-container">
        {isNewChat ? (
          // Empty Chat State
          <div className="empty-chat-state">
            <img src={PersibLogo} alt="Persib Logo" className="persib-logo" />
            <h1 className="welcome-title">Mulai obrolan baru dengan <span className="highlight">Maung Chat</span></h1>
            <p className="welcome-subtitle">Tanya seputar taktik, jadwal pertandingan, info pemain, atau ngobrolu seru bareng AI Legenda Persib.</p>

            <div className="suggested-questions">
              {suggestedQuestions.map((question, index) => (
                <button 
                  key={index}
                  className="question-card"
                  onClick={() => handleSuggestedQuestion(question)}
                  disabled={isLoading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          // Chat State
          <div className="chat-view">
            <div className="messages-container">
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
                >
                  <div className="message-bubble">
                    <p>{message.text}</p>
                    <span className="message-time">{formatTime(message.timestamp)}</span>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message bot-message">
                  <div className="message-bubble">
                    <p>Bot sedang mengetik...</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Input Form */}
        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Tanya Pak Robby tentang taktik..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="send-button" disabled={isLoading}>
            ▶
          </button>
        </form>
      </main>
    </div>
  )
}

export default Chatbot
