import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Guardia de administracion: solo admins pueden acceder
export default function AdminOnlyRoute({ children }) {
  const { usuario, cargando } = useAuth()

  if (cargando) return <p className="cargando">Cargando...</p>
  if (!usuario) return <Navigate to="/login" replace />
  // Si no es admin, redirige al dashboard en lugar del login
  if (usuario.rol !== "admin_total" && usuario.rol !== "admin_empresa") {
    return <Navigate to="/dashboard" replace />
  }

  return children
}
