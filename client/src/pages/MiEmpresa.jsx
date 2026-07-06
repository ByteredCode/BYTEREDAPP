import { useEffect, useState } from "react"
import { useAuth } from "../context/AuthContext"
import api from "../api/axios"

const SERVICIOS_ETIQUETAS = {
  scrum: "Scrum",
  tickets: "Tickets de soporte",
  documentacion: "Documentación DPD/ISO",
  redireccion: "Redirección a web externa",
  gestion_usuarios: "Gestión de usuarios",
}

export default function MiEmpresa() {
  const { usuario } = useAuth()
  const [empresa, setEmpresa] = useState(null)
  const [servicios, setServicios] = useState([])
  const [editando, setEditando] = useState(false)
  const [nombre, setNombre] = useState("")
  const [web, setWeb] = useState("")
  const [error, setError] = useState("")
  const puedeEditar = usuario?.rol?.startsWith("admin")

  useEffect(() => {
    Promise.all([
      api.get("/empresa/mi-empresa"),
      api.get("/empresa/mi-empresa/servicios"),
    ])
      .then(([resEmpresa, resServicios]) => {
        setEmpresa(resEmpresa.data)
        setNombre(resEmpresa.data.nombre)
        setWeb(resEmpresa.data.web || "")
        setServicios(resServicios.data)
      })
      .catch(() => setError("Error al cargar datos de la empresa"))
  }, [])

  // guardar es async porque la petición PATCH es una operación I/O que no debe bloquear la UI;
  // el usuario puede seguir interactuando mientras se envía la petición al backend.
  async function guardar(e) {
    e.preventDefault()
    // Se limpia el error previo antes de intentar guardar, para que no se acumulen mensajes.
    setError("")
    try {
      // PATCH en vez de PUT porque solo se envían los campos modificables (nombre y web),
      // no el objeto completo de la empresa (principio de granularidad en APIs REST).
      const res = await api.patch("/empresa/mi-empresa", { nombre, web })
      setEmpresa(res.data)
      // Al guardar exitosamente se vuelve a la vista de solo lectura.
      setEditando(false)
    } catch {
      setError("Error al guardar los cambios")
    }
  }

  // Mientras no hay datos de la empresa se muestra un placeholder de carga;
  // esto evita que el resto del JSX intente acceder a propiedades de null.
  if (!empresa) {
    return <div className="empresa-portal"><p>Cargando...</p></div>
  }

  return (
    <div className="empresa-portal">
      <h1>Mi Empresa</h1>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Renderizado condicional: si editando es true se muestra el formulario;
          si es false se muestra la vista de solo lectura. Esto evita tener dos rutas
          distintas y mantiene toda la lógica de empresa en un solo componente. */}
      {editando ? (
        <form onSubmit={guardar} className="empresa-form">
          <label>
            Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </label>
          <label>
            Sitio web
            {/* placeholder="https://" orienta al usuario sobre el formato esperado
                sin necesidad de una etiqueta de ayuda adicional. */}
            <input value={web} onChange={(e) => setWeb(e.target.value)} placeholder="https://" />
          </label>
          <div className="form-actions">
            <button type="submit" className="btn">Guardar</button>
            {/* El botón Cancelar es de tipo "button" (no "submit") para que no active
                la validación del formulario ni envíe datos accidentalmente. */}
            <button type="button" className="btn btn-secundario" onClick={() => setEditando(false)}>Cancelar</button>
          </div>
        </form>
      ) : (
        <div className="empresa-info">
          <p><strong>Nombre:</strong> {empresa.nombre}</p>
          <p><strong>Código:</strong> {empresa.codigo_empresa}</p>
          {/* web || "—" para mostrar un guión si la empresa no tiene sitio web registrado,
              en vez de dejar el campo vacío o mostrar "null". */}
          <p><strong>Sitio web:</strong> {empresa.web || "—"}</p>
          {puedeEditar && (
            <button className="btn" onClick={() => setEditando(true)}>Editar</button>
          )}

          <h2>Servicios contratados</h2>
          <div className="servicios-lista">
            {servicios.map((s) => (
              <div key={s.servicio} className="servicio-item">
                <span className="servicio-nombre">
                  {SERVICIOS_ETIQUETAS[s.servicio] || s.servicio}
                </span>
                <span className={s.activo ? "estado-activo" : "estado-inactivo"}>
                  {s.activo ? "Activado" : "Desactivado"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
