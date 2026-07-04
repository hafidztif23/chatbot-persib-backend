const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Helper untuk get token dari localStorage
const getToken = () => {
  return localStorage.getItem('access_token')
}

// Helper untuk set token ke localStorage
const setToken = (token) => {
  localStorage.setItem('access_token', token)
}

// Helper untuk remove token
const removeToken = () => {
  localStorage.removeItem('access_token')
}

// Helper untuk get user dari localStorage
const getUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

// Helper untuk set user ke localStorage
const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user))
}

// Helper untuk remove user
const removeUser = () => {
  localStorage.removeItem('user')
}

// Generic fetch function dengan auth
const apiFetch = async (endpoint, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  })

  // Jika 401, clear token dan redirect ke login
  if (response.status === 401) {
    removeToken()
    removeUser()
    window.location.href = '/login'
  }

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || data.message || 'Error dari server')
  }

  return data
}

// ============ AUTH API ============

export const authAPI = {
  // Register
  register: async (formData) => {
    const payload = {
      nama_lengkap: formData.fullname,
      nik: formData.nik,
      email: formData.email,
      nomor_telepon: formData.nomor_telepon,
      tanggal_lahir: formData.tanggal_lahir,
      jenis_kelamin: formData.jenis_kelamin,
      kota: formData.kota,
      password: formData.password,
    }

    const response = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    return response
  },

  // Login
  login: async (email, password) => {
    const response = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    // Simpan token dan user info
    setToken(response.access_token)
    setUser(response.account)

    return response
  },

  // Get profile
  getProfile: async () => {
    return await apiFetch('/auth/me', {
      method: 'GET',
    })
  },

  // Update profile
  updateProfile: async (data) => {
    return await apiFetch('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // Logout
  logout: () => {
    removeToken()
    removeUser()
    window.location.href = '/'
  },
}

// ============ CHAT API ============

export const chatAPI = {
  // Send message
  sendMessage: async (query) => {
    return await apiFetch('/chat', {
      method: 'POST',
      body: JSON.stringify({ query }),
    })
  },
}

// ============ TOKEN MANAGEMENT ============

const isLoggedIn = () => {
  return !!getToken()
}

export const tokenManager = {
  getToken,
  setToken,
  removeToken,
  getUser,
  setUser,
  removeUser,
  isLoggedIn,
}
