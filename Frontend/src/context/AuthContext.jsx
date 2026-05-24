import { createContext, useState, useEffect } from 'react'
import api from '../api/axios'

export const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('hdm_token')
    const savedUser = localStorage.getItem('hdm_user')
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        setUser(userData)
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } catch {
        localStorage.removeItem('hdm_token')
        localStorage.removeItem('hdm_user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    const token = data.data.access_token
    localStorage.setItem('hdm_token', token)
    const userData = { email, username: data.data.username, role: data.data.role }
    localStorage.setItem('hdm_user', JSON.stringify(userData))
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    setUser(userData)
    return data
  }

  const register = async (email, username, password) => {
    const { data } = await api.post('/auth/register', { email, username, password })
    const token = data.data.access_token
    localStorage.setItem('hdm_token', token)
    const userData = { email, username, role: 'user' }
    localStorage.setItem('hdm_user', JSON.stringify(userData))
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    setUser(userData)
    return data
  }

  const logout = () => {
    localStorage.removeItem('hdm_token')
    localStorage.removeItem('hdm_user')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}