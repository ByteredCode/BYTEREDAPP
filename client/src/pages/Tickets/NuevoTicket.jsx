import { useState } from "react"
import api from "../../api/axios"

// Formulario público de tickets (no requiere autenticación)
// Separamos intencionadamente el estado del frontend del envío:
// así podemos resetear el formulario sin tener que recargar la página
export default function NuevoTicket() {
  const [form, setForm] = useState({
    nombre_contacto: "",
    correo_contacto: "",
    asunto: "",
    nivel_importancia: "Media",
    mensaje: "",
    codigo_empresa: "",
  })
  // Estado "enviado" nos permite cambiar la vista completa sin usar
  // React Router; es un flag interno del componente
  const [enviado, setEnviado] = useState(false)
  const [error, setError] = useState("")
  // cargando bloquea el botón de envío para evitar dobles envíos
  // mientras la petición está en curso
  const [cargando, setCargando] = useState(false)

  async function enviar(e) {
    e.preventDefault()
    // Limpiamos errores previos antes de cada intento para que
    // el usuario no vea mensajes fantasma de envíos anteriores
    setError("")
    setCargando(true)
    try {
      // Hacemos una copia superficial para no mutar el estado original
      // mientras transformamos los datos para el backend
      const payload = { ...form }
      // Convertir campos vacios a null para el backend
      if (!payload.nombre_contacto) payload.nombre_contacto = null
      if (!payload.asunto) payload.asunto = null
      // El backend espera un entero, no un string del input
      payload.codigo_empresa = Number(payload.codigo_empresa)
      await api.post("/tickets", payload)
      // Marcamos como enviado para mostrar la pantalla de confirmación;
      // el formulario original se descarta, evitando reenvíos accidentales
      setEnviado(true)
    } catch (err) {
      setError(err.response?.data?.detail || "Error al enviar ticket")
    } finally {
      // finally asegura que el botón se desbloquee incluso si hay
      // una excepción inesperada (error de red, parseo, etc.)
      setCargando(false)
    }
  }

  // Pantalla de éxito: ocupa todo el render para que el usuario no
  // pueda reenviar accidentalmente el mismo formulario con doble clic
  if (enviado) {
    return (
      <div className="ticket-exito">
        <h2>Ticket enviado</h2>
        <p>Hemos recibido tu mensaje. Te responderemos pronto.</p>
        {/* Al resetear el estado volvemos al formulario limpio;
            no usamos navigate porque queremos mantener la misma URL
            (este componente es la propia ruta /tickets/nuevo) */}
        <button className="btn-primary" onClick={() => { setEnviado(false); setForm({ nombre_contacto: "", correo_contacto: "", asunto: "", nivel_importancia: "Media", mensaje: "", codigo_empresa: "" }) }}>
          Enviar otro
        </button>
      </div>
    )
  }

  return (
    <div className="ticket-form-container">
      <h2>Enviar ticket de soporte</h2>
      <form className="ticket-form" onSubmit={enviar}>
        {/* El mensaje de error se muestra condicionalmente solo cuando
            hay contenido, evitando espacios vacíos en el layout */}
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
        <div className="campo-row">
          <div className="campo">
            <label>Importancia</label>
            <select value={form.nivel_importancia} onChange={(e) => setForm({ ...form, nivel_importancia: e.target.value })}>
              <option value="Baja">Baja</option>
              <option value="Media">Media</option>
              <option value="Alta">Alta</option>
              <option value="Critica">Crítica</option>
            </select>
          </div>
          <div className="campo">
            <label>Código de empresa</label>
            <input type="number" value={form.codigo_empresa} onChange={(e) => setForm({ ...form, codigo_empresa: e.target.value })} required />
          </div>
        </div>
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
