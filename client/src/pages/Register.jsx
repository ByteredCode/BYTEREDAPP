import { useState } from "react"
import { useNavigate } from "react-router-dom"
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
    <form onSubmit={handleSubmit}>
      <h1>Registrarse</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input
        type="text"
        placeholder="Nombre"
        value={nombre}
        onChange={(e) => setNombre(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Correo"
        value={correo}
        onChange={(e) => setCorreo(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Contrasena"
        value={contrasena}
        onChange={(e) => setContrasena(e.target.value)}
        required
      />
      <input
        type="number"
        placeholder="Codigo de empresa"
        value={codigoEmpresa}
        onChange={(e) => setCodigoEmpresa(e.target.value)}
        required
      />
      <button type="submit">Registrarse</button>
      <p>
        <a href="/login">Ya tengo cuenta</a>
      </p>
    </form>
  )
}
