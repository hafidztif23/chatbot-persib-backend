import React, { useState } from 'react'
import './AuthForm.css'
import PersibLogo from '../image/landingpagepersib.jpeg'
import { useAuth } from '../hooks/useAuth'

function SignUp() {
  const [formData, setFormData] = useState({
    fullname: '',
    nik: '',
    email: '',
    nomor_telepon: '',
    tanggal_lahir: '',
    jenis_kelamin: 'Pria',
    kota: '',
    password: '',
    agreeTerms: false
  })

  const [showPassword, setShowPassword] = useState(false)
  const { register, isLoading, error } = useAuth()
  const [successMessage, setSuccessMessage] = useState('')
  const [validationErrors, setValidationErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    // Clear validation error untuk field yang sedang diubah
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const errors = {}

    if (formData.fullname.trim() === '') {
      errors.fullname = 'Nama lengkap harus diisi'
    }

    if (formData.nik.trim() === '') {
      errors.nik = 'NIK harus diisi'
    } else if (!/^\d{16}$/.test(formData.nik)) {
      errors.nik = 'NIK harus 16 digit angka'
    }

    if (formData.email.trim() === '') {
      errors.email = 'Email harus diisi'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Format email tidak valid'
    }

    if (formData.nomor_telepon.trim() === '') {
      errors.nomor_telepon = 'Nomor telepon harus diisi'
    } else if (!/^[\d\-\+]{8,13}$/.test(formData.nomor_telepon.replace(/\s/g, ''))) {
      errors.nomor_telepon = 'Nomor telepon harus 8-13 karakter (angka, +, atau -)'
    }

    if (formData.tanggal_lahir.trim() === '') {
      errors.tanggal_lahir = 'Tanggal lahir harus diisi'
    }

    if (formData.jenis_kelamin === '') {
      errors.jenis_kelamin = 'Jenis kelamin harus dipilih'
    }

    if (formData.password.trim() === '') {
      errors.password = 'Password harus diisi'
    } else if (formData.password.length < 8) {
      errors.password = 'Password minimal 8 karakter'
    }

    if (!formData.agreeTerms) {
      errors.agreeTerms = 'Anda harus setuju dengan terms & conditions'
    }

    return errors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSuccessMessage('')
    
    const errors = validateForm()
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors)
      return
    }

    try {
      await register(formData)
      setSuccessMessage('Registrasi berhasil! Redirect ke login...')
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500)
    } catch (err) {
      // Error sudah ditangani di useAuth
      console.error('Register error:', err)
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
          <h2>Create an Account</h2>
          <p>Kindly fill in your details to create an account</p>

          {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '14px' }}>⚠️ {error}</div>}
          {successMessage && <div style={{ color: 'green', marginBottom: '10px', fontSize: '14px' }}>✓ {successMessage}</div>}

          <form onSubmit={handleSubmit} className="auth-form" style={{ maxHeight: '600px', overflowY: 'auto', paddingRight: '10px' }}>
            
            {/* Nama Lengkap */}
            <div className="form-group">
              <label>Nama Lengkap*</label>
              <input
                type="text"
                name="fullname"
                placeholder="Masukkan nama lengkap"
                value={formData.fullname}
                onChange={handleChange}
                disabled={isLoading}
              />
              {validationErrors.fullname && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.fullname}</span>}
            </div>

            {/* NIK */}
            <div className="form-group">
              <label>NIK (16 digit)*</label>
              <input
                type="text"
                name="nik"
                placeholder="Masukkan NIK (16 digit)"
                value={formData.nik}
                onChange={handleChange}
                disabled={isLoading}
                maxLength="16"
              />
              {validationErrors.nik && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.nik}</span>}
            </div>

            {/* Email */}
            <div className="form-group">
              <label>Email*</label>
              <input
                type="email"
                name="email"
                placeholder="Masukkan email"
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
              />
              {validationErrors.email && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.email}</span>}
            </div>

            {/* Nomor Telepon */}
            <div className="form-group">
              <label>Nomor Telepon (8-13 digit)*</label>
              <input
                type="tel"
                name="nomor_telepon"
                placeholder="08123456789 atau +62812345678"
                value={formData.nomor_telepon}
                onChange={handleChange}
                disabled={isLoading}
              />
              {validationErrors.nomor_telepon && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.nomor_telepon}</span>}
            </div>

            {/* Tanggal Lahir */}
            <div className="form-group">
              <label>Tanggal Lahir*</label>
              <input
                type="date"
                name="tanggal_lahir"
                value={formData.tanggal_lahir}
                onChange={handleChange}
                disabled={isLoading}
              />
              {validationErrors.tanggal_lahir && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.tanggal_lahir}</span>}
            </div>

            {/* Jenis Kelamin */}
            <div className="form-group">
              <label>Jenis Kelamin*</label>
              <select
                name="jenis_kelamin"
                value={formData.jenis_kelamin}
                onChange={handleChange}
                disabled={isLoading}
                style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ddd' }}
              >
                <option value="Pria">Pria</option>
                <option value="Wanita">Wanita</option>
              </select>
              {validationErrors.jenis_kelamin && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.jenis_kelamin}</span>}
            </div>

            {/* Kota (Optional) */}
            <div className="form-group">
              <label>Kota (Opsional)</label>
              <input
                type="text"
                name="kota"
                placeholder="Masukkan kota (opsional)"
                value={formData.kota}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            {/* Password */}
            <div className="form-group">
              <label>Password (minimal 8 karakter)*</label>
              <div className="password-field">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Masukkan password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
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
              {validationErrors.password && <span style={{ color: 'red', fontSize: '12px' }}>⚠️ {validationErrors.password}</span>}
            </div>

            {/* Terms & Conditions */}
            <div className="form-group checkbox">
              <input
                type="checkbox"
                name="agreeTerms"
                id="agreeTerms"
                checked={formData.agreeTerms}
                onChange={handleChange}
                disabled={isLoading}
              />
              <label htmlFor="agreeTerms">I agree to terms & conditions*</label>
              {validationErrors.agreeTerms && <span style={{ color: 'red', fontSize: '12px', display: 'block', marginTop: '5px' }}>⚠️ {validationErrors.agreeTerms}</span>}
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Sign up'}
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
            Already have an Account? <a href="/login">Login</a>
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

export default SignUp
