import { useState, useEffect } from "react"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"

export default function NuevoTicket() {
  const { usuario } = useAuth()
  const [form, setForm] = useState({
    nombre_contacto: "",
    correo_contacto: "",
    asunto: "",
    mensaje: "",
    codigo_empresa: "",
  })
  const [empresas, setEmpresas] = useState([])
  const [enviado, setEnviado] = useState(false)
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)

  const esAnonimo = !usuario

  useEffect(() => {
    if (esAnonimo) {
      api.get("/tickets/empresas")
        .then((res) => setEmpresas(res.data))
        .catch(() => {})
    }
  }, [esAnonimo])

  async function enviar(e) {
    e.preventDefault()
    setError("")
    setCargando(true)
    try {
      const payload = { ...form }
      if (!payload.nombre_contacto) payload.nombre_contacto = null
      if (!payload.asunto) payload.asunto = null
      if (usuario) {
        payload.codigo_empresa = usuario.codigo_empresa
      } else {
        payload.codigo_empresa = Number(payload.codigo_empresa)
      }
      await api.post("/tickets", payload)
      setEnviado(true)
    } catch (err) {
      setError(err.response?.data?.detail || "Error al enviar ticket")
    } finally {
      setCargando(false)
    }
  }

  if (enviado) {
    return (
      <div className="ticket-exito">
        <h2>Ticket enviado</h2>
        <p>Hemos recibido tu mensaje. Te responderemos pronto.</p>
        <button className="btn-primary" onClick={() => { setEnviado(false); setForm({ nombre_contacto: "", correo_contacto: "", asunto: "", mensaje: "", codigo_empresa: "" }) }}>
          Enviar otro
        </button>
      </div>
    )
  }

  return (
    <div className="ticket-form-container">
      <h2>Enviar ticket de soporte</h2>
      <form className="ticket-form" onSubmit={enviar}>
        {error && <div className="error">{error}</div>}
        <div className="campo">
          <label>Nombre (opcional)</label>
          <input value={form.nombre_contacto} onChange={(e) => setForm({ ...form, nombre_contacto: e.target.value })} />
        </div>
        <div className="campo">
          <label>Correo electrónico</label>
          <input type="email" value={form.correo_contacto} onChange={(e) => setForm({ ...form, correo_contacto: e.target.value })} required />
        </div>
        <div className="campo">
          <label>Asunto</label>
          <input value={form.asunto} onChange={(e) => setForm({ ...form, asunto: e.target.value })} />
        </div>
        {!esAnonimo && (
          <div className="campo">
            <label>Empresa</label>
            <input type="text" value={usuario?.codigo_empresa || ""} disabled />
            <small>Tu empresa se asigna automáticamente</small>
          </div>
        )}
        {esAnonimo && (
          <div className="campo">
            <label>Empresa</label>
            <select value={form.codigo_empresa} onChange={(e) => setForm({ ...form, codigo_empresa: e.target.value })} required>
              <option value="">Selecciona empresa</option>
              {empresas.map((emp) => (
                <option key={emp.codigo_empresa} value={emp.codigo_empresa}>{emp.nombre}</option>
              ))}
            </select>
          </div>
        )}
        <div className="campo">
          <label>Mensaje</label>
          <textarea rows="5" value={form.mensaje} onChange={(e) => setForm({ ...form, mensaje: e.target.value })} required />
        </div>
        <button className="btn-primary" type="submit" disabled={cargando}>
          {cargando ? "Enviando..." : "Enviar ticket"}
        </button>
      </form>
    </div>
  )
}
