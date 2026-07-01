import { useEffect, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import api from "../../api/axios"
import { useAuth } from "../../context/AuthContext"

// Solo roles asignables desde el panel; admin_total se omite porque es un rol reservado
// que solo se asigna desde la base de datos (no debe poder crearse desde el frontend por seguridad)
const ROLES = [
  { valor: "usuario", etiqueta: "Usuario" },
  { valor: "admin_empresa", etiqueta: "Admin empresa" },
]

export default function UsuarioForm() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { usuario: usuarioActual } = useAuth()
  // Si hay id en la URL estamos editando; si no, creando uno nuevo
  const esEdicion = Boolean(id)

  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [nombre, setNombre] = useState("")
  const [rol, setRol] = useState("usuario")
  // La empresa se pre-rellena con el query param ?empresa= o la empresa del usuario actual
  const [codigoEmpresa, setCodigoEmpresa] = useState(
    searchParams.get("empresa") || usuarioActual?.codigo_empresa || ""
  )
  // Solo mostramos spinner de carga cuando editamos, porque en creación no hay datos que precargar
  const [cargando, setCargando] = useState(esEdicion)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState("")

  // Guardamos esta comprobación en una constante para evitar recalcular el string cada render y centralizar la lógica de permisos
  const esAdminTotal = usuarioActual?.rol === "admin_total"

  useEffect(() => {
    // Si no hay id (creación) no precargamos nada
    if (!id) return

    // Usamos async/await en vez de .then() porque la lógica tiene bifurcaciones (if/else) que serían más difíciles de leer con promesas encadenadas
    const cargarUsuario = async () => {
      try {
        // Primero obtenemos la empresa del usuario actual o buscamos en todas
        let endpoint;
        if (esAdminTotal) {
          // El admin_total puede buscar el usuario en la lista global primero (más rápido)
          const resUsuarios = await api.get("/admin/usuarios")
          const encontrado = resUsuarios.data.find(
            (u) => String(u.codigo_usuario) === String(id)
          )
          if (encontrado) {
            llenarFormulario(encontrado)
            return
          }
          // Si no lo encontramos en la lista global, buscamos por empresa
          endpoint = `/admin/empresas/${codigoEmpresa}/usuarios`
        } else {
          // Un admin_empresa solo puede ver usuarios de su propia empresa
          endpoint = `/admin/empresas/${usuarioActual.codigo_empresa}/usuarios`
        }

        const res = await api.get(endpoint)
        const encontrado = res.data.find(
          (u) => String(u.codigo_usuario) === String(id)
        )
        if (encontrado) {
          llenarFormulario(encontrado)
        } else {
          setError("Usuario no encontrado")
        }
      } catch (err) {
        setError(err.response?.data?.detalle || "Error al cargar usuario")
      } finally {
        setCargando(false)
      }
    }

    cargarUsuario()
    // Desactivamos advertencia porque no queremos que se re-ejecute al cambiar codigoEmpresa
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const llenarFormulario = (user) => {
    setCorreo(user.correo || "")
    setNombre(user.nombre || "")
    setRol(user.rol || "usuario")
    setCodigoEmpresa(user.codigo_empresa || "")
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!correo.trim() || !nombre.trim()) {
      setError("Correo y nombre son obligatorios")
      return
    }
    if (!esEdicion && !contrasena.trim()) {
      setError("La contrasena es obligatoria en creacion")
      return
    }

    setEnviando(true)
    setError("")

    try {
      const datos = {
        correo: correo.trim(),
        nombre: nombre.trim(),
        rol,
        codigo_empresa: codigoEmpresa || undefined,
      }
      if (contrasena.trim()) {
        datos.contrasena = contrasena
      }

      // PUT es idempotente (actualiza un recurso existente), POST crea uno nuevo — usamos cada verbo HTTP según su semántica REST
      if (esEdicion) {
        await api.put(`/admin/usuarios/${id}`, datos)
      } else {
        await api.post("/admin/usuarios", datos)
      }
      navigate("/admin/usuarios")
    } catch (err) {
      setError(err.response?.data?.detalle || "Error al guardar usuario")
    } finally {
      setEnviando(false)
    }
  }

  if (cargando) return <p className="cargando">Cargando usuario...</p>

  return (
    <div className="pagina-admin">
      <h1>{esEdicion ? "Editar usuario" : "Nuevo usuario"}</h1>

      {error && <p className="error">{error}</p>}

      <form onSubmit={handleSubmit} className="form-admin">
        <div className="form-campo">
          <label htmlFor="correo">Correo *</label>
          <input
            id="correo"
            type="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            placeholder="correo@ejemplo.com"
          />
        </div>

        <div className="form-campo">
          <label htmlFor="nombre">Nombre *</label>
          <input
            id="nombre"
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            placeholder="Nombre completo"
          />
        </div>

        <div className="form-campo">
          <label htmlFor="contrasena">
            Contrasena {esEdicion ? "(dejar vacio para mantener)" : "*"}
          </label>
          <input
            id="contrasena"
            type="password"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            required={!esEdicion}
            placeholder={esEdicion ? "Nueva contrasena (opcional)" : "Contrasena"}
          />
        </div>

        <div className="form-campo">
          <label htmlFor="rol">Rol</label>
          <select
            id="rol"
            value={rol}
            onChange={(e) => setRol(e.target.value)}
          >
            {ROLES.map((r) => (
              <option key={r.valor} value={r.valor}>
                {r.etiqueta}
              </option>
            ))}
          </select>
        </div>

        {/* Solo el admin_total puede cambiar la empresa del usuario; un admin_empresa está limitado a su tenant por diseño */}
        {esAdminTotal && (
          <div className="form-campo">
            <label htmlFor="codigoEmpresa">Codigo de empresa</label>
            <input
              id="codigoEmpresa"
              type="text"
              value={codigoEmpresa}
              onChange={(e) => setCodigoEmpresa(e.target.value)}
              placeholder="Obligatorio para admin_total"
            />
          </div>
        )}

        <div className="form-acciones">
          <button
            type="button"
            className="btn btn-secundario"
            onClick={() => navigate("/admin/usuarios")}
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
                ? "Actualizar usuario"
                : "Crear usuario"}
          </button>
        </div>
      </form>
    </div>
  )
}
