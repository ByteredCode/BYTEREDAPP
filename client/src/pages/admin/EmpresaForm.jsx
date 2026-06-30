import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import api from "../../api/axios"

export default function EmpresaForm() {
  // Extraemos el id de la URL con useParams porque este componente se renderiza
  // tanto para crear (sin id) como para editar (con /:id); así evitamos recibir
  // el id por props y el componente es más independiente del padre.
  const { id } = useParams()
  const navigate = useNavigate()
  // Convertimos el id a booleano: si existe, es edición; si es undefined, es alta.
  // Esto evita comparar con null/undefined en cada if del render.
  const esEdicion = Boolean(id)

  const [nombre, setNombre] = useState("")
  const [web, setWeb] = useState("")
  // Solo mostramos el spinner de carga cuando estamos en modo edición,
  // porque en creación no hay datos previos que recuperar del servidor.
  const [cargando, setCargando] = useState(esEdicion)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    // Si no hay id significa que estamos en creación; no necesitamos fetch previo.
    if (!id) return
    api
      .get(`/admin/empresas/${id}`)
      .then((res) => {
        setNombre(res.data.nombre || "")
        setWeb(res.data.web || "")
      })
      .catch((err) => {
        setError(err.response?.data?.detalle || "Error al cargar empresa")
      })
      .finally(() => setCargando(false))
  }, [id])

  const handleSubmit = async (e) => {
    e.preventDefault()
    // Validación temprana: cortamos el envío si el nombre está vacío,
    // así ahorramos una petición HTTP que el backend rechazaría igualmente.
    if (!nombre.trim()) {
      setError("El nombre es obligatorio")
      return
    }
    setEnviando(true)
    setError("")

    try {
      // Enviamos web.trim() o null en vez de cadena vacía para que el backend
      // guarde NULL en la BD en lugar de un string vacío, que es más semántico.
      const datos = { nombre: nombre.trim(), web: web.trim() || null }
      // PUT vs POST según si estamos editando o creando: así respetamos la
      // idempotencia REST (PUT es idempotente, POST no) y el backend sabe
      // exactamente qué operación realizar sin necesidad de lógica extra.
      if (esEdicion) {
        await api.put(`/admin/empresas/${id}`, datos)
      } else {
        await api.post("/admin/empresas", datos)
      }
      // Redirigimos al listado solo si la operación fue exitosa, así el
      // usuario no se queda en el formulario con datos posiblemente inconsistentes.
      navigate("/admin/empresas")
    } catch (err) {
      setError(err.response?.data?.detalle || "Error al guardar empresa")
    } finally {
      // finally asegura que el botón se reactive incluso si el catch lanza
      // un error inesperado que no capturamos (ej. error de red).
      setEnviando(false)
    }
  }

  if (cargando) return <p className="cargando">Cargando empresa...</p>

  return (
    <div className="pagina-admin">
      <h1>{esEdicion ? "Editar empresa" : "Nueva empresa"}</h1>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit} className="form-admin">
        <div className="form-campo">
          <label htmlFor="nombre">Nombre *</label>
          {/* required delega la validación al navegador y evita tener que
              mostrar un error personalizado para un caso tan básico como
              "el nombre está vacío". */}
          <input
            id="nombre"
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            placeholder="Nombre de la empresa"
          />
        </div>

        <div className="form-campo">
          <label htmlFor="web">Web</label>
          {/* type="url" activa la validación nativa del navegador para URLs,
              ahorrando una comprobación manual con regex en el frontend. */}
          <input
            id="web"
            type="url"
            value={web}
            onChange={(e) => setWeb(e.target.value)}
            placeholder="https://ejemplo.com"
          />
        </div>

        <div className="form-acciones">
          <button
            type="button"
            className="btn btn-secundario"
            onClick={() => navigate("/admin/empresas")}
          >
            Volver
          </button>
          <button
            type="submit"
            className="btn btn-primario"
            disabled={enviando}
          >
            {enviando
              ? "Guardando..."
              : esEdicion
                ? "Actualizar empresa"
                : "Crear empresa"}
          </button>
        </div>
      </form>
    </div>
  )
}
