import React, { createContext, useContext, useState } from 'react'
import { authAPI, tokenManager } from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUserState] = useState(tokenManager.getUser())
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const updateUser = (newUser) => {
    tokenManager.setUser(newUser)
    setUserState(newUser)
  }

  const login = async (email, password) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await authAPI.login(email, password)
      setUserState(response.account)
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
    setUserState(null)
    authAPI.logout()
  }

  const isLoggedIn = () => {
    return tokenManager.isLoggedIn()
  }

  return React.createElement(
    AuthContext.Provider,
    { value: { user, isLoading, error, login, register, logout, isLoggedIn, updateUser } },
    children
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
