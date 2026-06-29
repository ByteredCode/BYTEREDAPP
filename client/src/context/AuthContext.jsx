import { createContext, useContext, useState, useEffect } from "react"
import api from "../api/axios"

// Contexto global de autenticacion para toda la aplicacion
export const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)  // Mientras se verifica la sesion

  // Al montar la app, verificar si hay un token valido en localStorage
  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      api
        .get("/auth/me")
        .then((res) => setUsuario(res.data))
        .catch(() => {
          // Token invalido/expirado: limpiar y redirigir
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
        })
        .finally(() => setCargando(false))
    } else {
      setCargando(false)
    }
  }, [])

  const login = async (correo, contrasena) => {
    const res = await api.post("/auth/login", { correo, contrasena })
    localStorage.setItem("access_token", res.data.access_token)
    localStorage.setItem("refresh_token", res.data.refresh_token)
    // Obtener datos completos del usuario despues del login
    const me = await api.get("/auth/me")
    setUsuario(me.data)
    return me.data
  }

  const logout = async () => {
    try {
      await api.post("/auth/logout")
    } catch {
      // Error al llamar al backend no debe impedir el logout local
    }
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook personalizado para acceder al contexto desde cualquier componente
export const useAuth = () => useContext(AuthContext)
