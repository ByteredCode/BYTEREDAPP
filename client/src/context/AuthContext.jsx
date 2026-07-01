import { createContext, useContext, useState, useEffect } from "react"
// Usamos axios con interceptores para que el token se adjunte automaticamente a cada peticion
import api from "../api/axios"

// Usamos Context API en vez de props para que cualquier componente hijo pueda leer la sesion sin recibirla explicitamente
export const AuthContext = createContext()

export function AuthProvider({ children }) {
  // Mantenemos el usuario en estado para que React re-renderice cuando inicie/cierre sesion
  const [usuario, setUsuario] = useState(null)
  // Arrancamos con 'cargando = true' para que la UI pueda mostrar un spinner antes de saber si hay sesion activa
  const [cargando, setCargando] = useState(true)

  // Solo se ejecuta al montar el provider ([] de dependencias) para restaurar la sesion del usuario si su token aun es valido
  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      // Pedimos al backend los datos del usuario asociado al token; si el token expiro el catch lo limpia
      api
        .get("/auth/me")
        .then((res) => setUsuario(res.data))
        .catch(() => {
          // Si el backend rechaza el token (expirado/invalido) borramos todo para que no queden residuos
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
        })
        .finally(() => setCargando(false))
    } else {
      // Sin token no hay sesion que restaurar, marcamos como listo inmediatamente
      setCargando(false)
    }
  }, [])

  const login = async (correo, contrasena) => {
    const res = await api.post("/auth/login", { correo, contrasena })
    localStorage.setItem("access_token", res.data.access_token)
    localStorage.setItem("refresh_token", res.data.refresh_token)
    setUsuario(res.data.usuario)
    return res.data.usuario
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token")
      if (refreshToken) {
        await api.post("/auth/logout", { refresh_token: refreshToken })
      }
    } catch {
      // Si el backend no responde, aun asi limpiamos el cliente para que el usuario no se quede atascado
    }
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUsuario(null)
  }

  return (
    // Exponemos el estado y las funciones para que cualquier descendiente los consuma con useAuth()
    <AuthContext.Provider value={{ usuario, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Encapsulamos useContext en un hook con nombre semantico para evitar importar createContext y useContext cada vez
export const useAuth = () => useContext(AuthContext)
