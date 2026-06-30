import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Guardia de autenticación: solo muestra las rutas hijas si hay sesión activa
export default function ProtectedRoute({ children }) {
  const { usuario, cargando } = useAuth()

  // Mientras se verifica el token JWT no redirigimos para evitar un "flash" de pantalla de login
  if (cargando) return <p>Cargando...</p>
  // Sin sesión activa redirigimos al login; `replace` evita que el usuario vuelva con "Atrás" a la ruta protegida
  if (!usuario) return <Navigate to="/login" replace />

  // Usuario autenticado: renderizamos el contenido protegido
  return children
}
