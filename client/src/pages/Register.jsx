import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api/axios"

export default function Register() {
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [nombre, setNombre] = useState("")
  const [codigoEmpresa, setCodigoEmpresa] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post("/auth/register", {
        correo,
        contrasena,
        nombre,
        codigo_empresa: Number(codigoEmpresa),
      })
      navigate("/login")
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrarse")
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Registrarse</h1>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="campo">
            <input
              type="text"
              placeholder="Nombre completo"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              required
            />
          </div>
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
          <div className="campo">
            <input
              type="number"
              placeholder="Código de empresa"
              value={codigoEmpresa}
              onChange={(e) => setCodigoEmpresa(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">Registrarse</button>
        </form>
        <div className="auth-link">
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </div>
      </div>
    </div>
  )
}
