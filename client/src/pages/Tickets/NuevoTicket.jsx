import { useState, useEffect, useRef } from "react"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"

const MAX_FOTOS = 3
const TIPOS_PERMITIDOS = ["image/jpeg", "image/png", "image/gif", "image/webp"]

export default function NuevoTicket() {
  const { usuario } = useAuth()
  const [form, setForm] = useState({
    nombre_contacto: "",
    correo_contacto: "",
    asunto: "",
    mensaje: "",
    codigo_empresa: "",
  })
  const [fotos, setFotos] = useState([])
  const [empresas, setEmpresas] = useState([])
  const [enviado, setEnviado] = useState(false)
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)
  const inputFotosRef = useRef()

  const esAnonimo = !usuario

  useEffect(() => {
    if (esAnonimo) {
      api.get("/tickets/empresas")
        .then((res) => setEmpresas(res.data))
        .catch(() => {})
    }
  }, [esAnonimo])

  function seleccionarFotos(e) {
    const archivos = Array.from(e.target.files || [])
    const nuevos = [...fotos, ...archivos].slice(0, MAX_FOTOS)
    const validos = nuevos.filter((f) => TIPOS_PERMITIDOS.includes(f.type))
    if (validos.length < nuevos.length) {
      setError("Solo se permiten fotos JPEG, PNG, GIF o WebP")
    } else {
      setError("")
    }
    setFotos(validos)
  }

  function eliminarFoto(idx) {
    setFotos((prev) => prev.filter((_, i) => i !== idx))
  }

  async function enviar(e) {
    e.preventDefault()
    setError("")
    setCargando(true)
    try {
      const fd = new FormData()
      fd.append("correo_contacto", form.correo_contacto)
      fd.append("mensaje", form.mensaje)
      fd.append("nivel_importancia", "Media")
      if (form.nombre_contacto) fd.append("nombre_contacto", form.nombre_contacto)
      if (form.asunto) fd.append("asunto", form.asunto)
      if (usuario) {
        fd.append("codigo_empresa", usuario.codigo_empresa)
      } else {
        fd.append("codigo_empresa", Number(form.codigo_empresa))
      }
      fotos.forEach((f) => fd.append("fotos", f))
      await api.post("/tickets", fd)
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
        <button className="btn-primary" onClick={() => {
          setEnviado(false)
          setFotos([])
          setForm({ nombre_contacto: "", correo_contacto: "", asunto: "", mensaje: "", codigo_empresa: "" })
        }}>
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

        {usuario && (
          <div className="campo">
            <label>Fotos (opcional, max {MAX_FOTOS})</label>
            <input
              ref={inputFotosRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              multiple
              onChange={seleccionarFotos}
              style={{ display: "none" }}
            />
            <button
              type="button"
              className="btn-secundario btn-sm"
              onClick={() => inputFotosRef.current?.click()}
              disabled={fotos.length >= MAX_FOTOS}
            >
              {fotos.length >= MAX_FOTOS ? "Maximo alcanzado" : "Adjuntar fotos"}
            </button>
            {fotos.length > 0 && (
              <div className="ticket-fotos-preview">
                {fotos.map((f, i) => (
                  <div key={i} className="ticket-foto-mini">
                    <img src={URL.createObjectURL(f)} alt={`Foto ${i + 1}`} />
                    <button type="button" className="ticket-foto-eliminar" onClick={() => eliminarFoto(i)}>
                      x
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <button className="btn-primary" type="submit" disabled={cargando}>
          {cargando ? "Enviando..." : "Enviar ticket"}
        </button>
      </form>
    </div>
  )
}
