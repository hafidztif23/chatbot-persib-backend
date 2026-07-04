import React, { useState } from 'react'
import './AuthForm.css'
import PersibLogo from '../image/landingpagepersib.jpeg'
import { useAuth } from '../hooks/useAuth'

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const [showPassword, setShowPassword] = useState(false)
  const { login, isLoading, error } = useAuth()
  const [successMessage, setSuccessMessage] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSuccessMessage('')
    
    try {
      await login(formData.email, formData.password)
      setSuccessMessage('Login berhasil! Redirect ke chatbot...')
      setTimeout(() => {
        window.location.href = '/chat'
      }, 1500)
    } catch (err) {
      // Error sudah ditangani di useAuth
      console.error('Login error:', err)
    }
  }

  return (
    <div className="auth-container">
      {/* Left Panel - Form */}
      <div className="auth-left">
        <div className="auth-header">
          <div className="auth-logo-icon">👤</div>
          <h1>MAUNG BOT</h1>
        </div>

        <div className="auth-form-container">
          <h2>Login</h2>
          <p>Add your credentials to log in</p>

          {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '14px' }}>⚠️ {error}</div>}
          {successMessage && <div style={{ color: 'green', marginBottom: '10px', fontSize: '14px' }}>✓ {successMessage}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>Your email*</label>
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
            </div>

            <div className="form-group">
              <label>Password*</label>
              <div className="password-field">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Enter password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                  required
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            <div className="form-group checkbox">
              <input type="checkbox" id="rememberMe" disabled={isLoading} />
              <label htmlFor="rememberMe">I agree to terms & conditions</label>
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Login'}
            </button>
          </form>

          <div className="auth-divider">
            <span>Or</span>
          </div>

          <button className="google-btn">
            <span className="google-icon">G</span>
            Register with Google
          </button>

          <p className="auth-footer">
            Don't have an Account? <a href="/signup">Sign up</a>
          </p>
        </div>
      </div>

      {/* Right Panel - Logo */}
      <div className="auth-right">
        <img src={PersibLogo} alt="Persib" className="auth-logo-image" />
      </div>
    </div>
  )
}

export default Login
