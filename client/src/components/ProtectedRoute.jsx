import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// Guardia de autenticacion: redirige al login si no hay sesion activa
export default function ProtectedRoute({ children }) {
  const { usuario, cargando } = useAuth()

  if (cargando) return <p>Cargando...</p>
  if (!usuario) return <Navigate to="/login" replace />  // replace evita volver con "Atras"

  return children
}
