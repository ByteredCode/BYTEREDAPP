import { useAuth } from "../context/AuthContext"

export default function Dashboard() {
  const { usuario, logout } = useAuth()

  return (
    <div>
      <h1>Panel de control</h1>
      <p>Bienvenido, {usuario?.nombre}</p>
      <p>Rol: {usuario?.rol}</p>
      <p>Empresa: {usuario?.codigo_empresa}</p>
      <button onClick={logout}>Cerrar sesion</button>
    </div>
  )
}
