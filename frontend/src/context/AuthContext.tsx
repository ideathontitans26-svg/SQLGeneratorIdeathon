import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { api } from '../api/client'

type AuthContextType = {
  email: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

const TOKEN_KEY = 'token'
const EMAIL_KEY = 'email'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(() => localStorage.getItem(EMAIL_KEY))
  const [loading, setLoading] = useState(true)

  const persistAuth = useCallback((token: string, userEmail: string) => {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(EMAIL_KEY, userEmail)
    setEmail(userEmail)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(EMAIL_KEY)
    setEmail(null)
  }, [])

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    api.getMe()
      .then((data) => {
        setEmail(data.email)
      })
      .catch(() => {
        logout()
      })
      .finally(() => setLoading(false))
  }, [logout])

  const login = useCallback(async (userEmail: string, password: string) => {
    const data = await api.login(userEmail, password)
    persistAuth(data.token, data.email)
  }, [persistAuth])

  const register = useCallback(async (userEmail: string, password: string) => {
    const data = await api.register(userEmail, password)
    persistAuth(data.token, data.email)
  }, [persistAuth])

  return (
    <AuthContext.Provider
      value={{
        email,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!email,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
