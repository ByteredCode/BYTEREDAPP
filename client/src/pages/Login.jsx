import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Login() {
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [error, setError] = useState("")
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(correo, contrasena)
      navigate("/dashboard")
    } catch {
      setError("Credenciales incorrectas")
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Iniciar sesión</h1>
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
          ¿No tienes cuenta? <Link to="/register">Registrarse</Link>
        </div>
      </div>
    </div>
  )
}
