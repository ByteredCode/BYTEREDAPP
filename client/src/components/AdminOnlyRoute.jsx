import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Guardia de ruta: verifica rol admin antes de renderizar; si no, redirige
export default function AdminOnlyRoute({ children }) {
  const { usuario, cargando } = useAuth()

  // Mientras se valida el token JWT mostramos un indicador para evitar parpadeos de redirección
  if (cargando) return <p className="cargando">Cargando...</p>
  // Sin sesión activa no tiene sentido mostrar nada protegido; redirigimos al login
  if (!usuario) return <Navigate to="/login" replace />
  // Usuario autenticado pero sin rol admin: redirigimos al dashboard en vez del login
  // porque ya está logueado y mandarlo al login sería confuso
  if (usuario.rol !== "admin_total" && usuario.rol !== "admin_empresa") {
    return <Navigate to="/dashboard" replace />
  }

  // Todo en orden: renderizamos el contenido hijo protegido
  return children
}
