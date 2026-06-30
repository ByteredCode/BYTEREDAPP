import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
// Se usa axios directamente en lugar del contexto de auth porque el registro
// es la única operación que no requiere JWT (el usuario aún no existe en sesión).
import api from "../api/axios"

export default function Register() {
  // Cada campo tiene su propio estado para poder validarlos por separado
  // y porque no dependen entre sí (no hay lógica cruzada entre ellos).
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [nombre, setNombre] = useState("")
  const [codigoEmpresa, setCodigoEmpresa] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  // Separar cada campo en su propio estado permite validarlos individualmente
  // y evita re-renderizados innecesarios del resto del formulario al escribir.
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // Se convierte codigoEmpresa a Number porque viene como string desde el input type="number".
      // El backend espera un entero para asociar al usuario con la empresa correcta (multi-tenant).
      await api.post("/auth/register", {
        correo,
        contrasena,
        nombre,
        codigo_empresa: Number(codigoEmpresa),
      })
      // Tras un registro exitoso se redirige al login en lugar de loguear directamente,
      // forzando al usuario a identificarse con sus nuevas credenciales.
      navigate("/login")
    } catch (err) {
      // Se muestra el mensaje de error que devuelve el backend (detail) o uno genérico
      // si no hay respuesta del servidor (ej. timeout, red caída).
      // Se encadena con || para tener un mensaje por defecto si el backend no responde
      // (ej. red caída, timeout), evitando que el usuario vea un error técnico crudo.
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
            {/* El código de empresa se pide como número porque es un identificador
                numérico en la BD que vincula al usuario con su tenant (multi-tenant). */}
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
          {/* Link de React Router en vez de <a> para evitar recarga completa;
              así se preserva el estado de la app y la experiencia es más fluida. */}
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </div>
      </div>
    </div>
  )
}
