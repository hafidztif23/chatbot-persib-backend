import { useState } from 'react'
import { authAPI, tokenManager } from '../services/api'

export const useAuth = () => {
  const [user, setUser] = useState(tokenManager.getUser())
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const login = async (email, password) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authAPI.login(email, password)
      setUser(response.account)
      return response
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (formData) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authAPI.register(formData)
      return response
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    authAPI.logout()
  }

  const isLoggedIn = () => {
    return tokenManager.isLoggedIn()
  }

  return {
    user,
    isLoading,
    error,
    login,
    register,
    logout,
    isLoggedIn,
  }
}
