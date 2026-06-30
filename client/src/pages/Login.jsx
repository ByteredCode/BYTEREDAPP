import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

// useAuth es un hook personalizado que accede al contexto de autenticación de React,
// evitando tener que pasar el token JWT por props entre componentes (prop drilling).
// El contexto mantiene el estado de sesión global y lo persiste en localStorage.
// El estado del formulario (correo, contraseña) se gestiona con hooks locales
// para que cada campo se valide de forma independiente sin depender de un store global.
export default function Login() {
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  // El error se maneja como estado local y no como parte del contexto de auth
  // porque es información transitoria que solo pertenece a esta vista.
  const [error, setError] = useState("")
  const { login } = useAuth()
  const navigate = useNavigate()

  // useNavigate en vez de window.location para cambiar de ruta sin recargar la página,
  // preservando el árbol de componentes, el estado de React y la memoización existente.
  // Se usa preventDefault para evitar que el navegador recargue la página
  // al enviar el formulario, y así controlar la navegación vía React Router.
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // login() es una función del contexto que maneja el almacenamiento del JWT
      // y la actualización del estado global de autenticación.
      await login(correo, contrasena)
      // Solo se redirige si el login fue exitoso; si falla, el catch captura el error.
      navigate("/dashboard")
    } catch {
      // Se muestra un mensaje genérico en lugar del error técnico real
      // para no filtrar información sensible (seguridad por oscuridad parcial).
      setError("Credenciales incorrectas")
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Iniciar sesión</h1>
        {/* El error se muestra condicionalmente para no ocupar espacio visual
            cuando no hay mensaje; al desaparecer solo, la UI no requiere interacción extra. */}
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="campo">
            <input
              type="email"
              placeholder="Correo electrónico"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              required
            />
          </div>
          <div className="campo">
            <input
              type="password"
              placeholder="Contraseña"
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">Entrar</button>
        </form>
        <div className="auth-link">
          {/* Link de React Router evita recarga completa y preserva el estado de la sesión */}
          Contacta con tu administrador para crear una cuenta
        </div>
      </div>
    </div>
  )
}
