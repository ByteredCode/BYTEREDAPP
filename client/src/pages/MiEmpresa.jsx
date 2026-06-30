import { useEffect, useState } from "react"
import { useAuth } from "../context/AuthContext"
import api from "../api/axios"

export default function MiEmpresa() {
  // usuario se obtiene del contexto de autenticación; contiene rol y datos del JWT
  // que determinan si el usuario puede editar (admin) o solo ver la información.
  const { usuario } = useAuth()
  const [empresa, setEmpresa] = useState(null)
  // editando controla qué vista se renderiza: formulario de edición vs. vista de solo lectura.
  const [editando, setEditando] = useState(false)
  const [nombre, setNombre] = useState("")
  const [web, setWeb] = useState("")
  const [error, setError] = useState("")
  // startsWith("admin") en vez de === "admin_total" para cubrir variantes de rol
  // (admin_empresa, admin_support, etc.) sin tener que actualizar el frontend al añadir nuevos roles.
  const puedeEditar = usuario?.rol?.startsWith("admin")

  // useEffect sin dependencias (array vacío) para que la carga de datos ocurra
  // solo una vez al montar el componente, no en cada re-renderizado.
  useEffect(() => {
    api.get("/empresa/mi-empresa").then((res) => {
      setEmpresa(res.data)
      // Se pre-rellenan los campos del formulario con los datos actuales de la empresa,
      // para que al editar el usuario vea los valores existentes como punto de partida.
      setNombre(res.data.nombre)
      // web puede venir null desde la BD; se usa || "" para no mostrar "null" en el input.
      setWeb(res.data.web || "")
    }).catch(() => setError("Error al cargar datos de la empresa"))
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
        </div>
      )}
    </div>
  )
}
