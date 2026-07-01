import { useState, useEffect, useCallback, useMemo, Fragment } from "react"
import api from "../../api/axios"
import { useToast } from "../../context/ToastContext"
import { useAuth } from "../../context/AuthContext"
import LoadingSpinner from "../../components/common/LoadingSpinner"
import Pagination from "../../components/common/Pagination"
import PermisosDoc from "./PermisosDoc"

// Administracion de documentos: subida, listado, descarga, permisos, eliminacion
export default function DocumentosAdmin() {
  // Usamos un contexto global de toasts en vez de un estado local para
  // que cualquier componente pueda lanzar notificaciones sin acoplarse
  const { showToast } = useToast()
  const { usuario } = useAuth()
  const esAdminTotal = usuario?.rol === "admin_total"
  // Mantenemos la lista completa en memoria para evitar llamadas
  // repetidas al backend cada vez que el usuario abre/cierra modales
  const [docs, setDocs] = useState([])
  const [mostrarSubida, setMostrarSubida] = useState(false)
  const [archivo, setArchivo] = useState(null)
  const [tipoDoc, setTipoDoc] = useState("")
  const [permisoDoc, setPermisoDoc] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [pagina, setPagina] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)
  const [empresas, setEmpresas] = useState([])
  const [empresaFiltro, setEmpresaFiltro] = useState("")

  // Cargar empresas solo para admin_total (para el filtro y la columna empresa)
  useEffect(() => {
    if (esAdminTotal) {
      api.get("/admin/empresas", { params: { limit: 200 } })
        .then((res) => setEmpresas(res.data.items || res.data))
        .catch(() => {})
    }
  }, [esAdminTotal])

  const fetchDocs = useCallback(async () => {
    setCargando(true)
    try {
      const params = { skip: (pagina - 1) * 50, limit: 50 }
      if (esAdminTotal && empresaFiltro) {
        params.empresa_filtro = Number(empresaFiltro)
      }
      const res = await api.get("/documentos", { params })
      setDocs(res.data.items)
      setTotalPaginas(Math.ceil(res.data.total / 50) || 1)
    } catch {
    } finally {
      setCargando(false)
    }
  }, [pagina, empresaFiltro])

  // El efecto depende de fetchDocs (memoizado) para recargar la lista
  // solo cuando la función cambie (nunca, en este caso)
  useEffect(() => { fetchDocs() }, [fetchDocs])

  // Mapa de codigo_empresa -> nombre para mostrar el nombre en la tabla
  const empresaMap = useMemo(() => {
    const map = {}
    empresas.forEach((e) => { map[e.codigo_empresa] = e.nombre })
    return map
  }, [empresas])

  // Agrupar documentos por tipo_documento para mostrar secciones separadas
  const docsAgrupados = useMemo(() => {
    const grupos = {}
    docs.forEach((d) => {
      const tipo = d.tipo_documento || "Otros"
      if (!grupos[tipo]) grupos[tipo] = []
      grupos[tipo].push(d)
    })
    return grupos
  }, [docs])

  const ordenTipos = ["DPD", "ISO", "Otros"]

  async function subir(e) {
    // Prevenimos el envío nativo del formulario para manejar
    // la petición con fetch/axios y mantener el control del estado
    e.preventDefault()
    if (!archivo) return
    try {
      // FormData permite combinar campos de texto con binarios (archivos)
      // en una misma petición HTTP multipart
      const fd = new FormData()
      fd.append("archivo", archivo)
      if (tipoDoc) fd.append("tipo_documento", tipoDoc)
      // Importante: no establecer Content-Type manualmente para multipart
      // Dejamos que el navegador añada el boundary automáticamente
      await api.post("/documentos", fd, { headers: { "Content-Type": "multipart/form-data" } })
      setMostrarSubida(false)
      setArchivo(null)
      setTipoDoc("")
      fetchDocs()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al subir")
    }
  }

  // Usamos confirm() nativo como protección rápida contra clics accidentales;
  // para acciones destructivas no necesitamos un modal personalizado
  async function eliminar(id) {
    // No actualizamos el estado local aquí; tras eliminar se invoca
    // fetchDocs() que resincroniza con el servidor, evitando
    // inconsistencias si otro usuario borró el mismo documento antes
    if (!confirm("¿Eliminar documento?")) return
    try {
      await api.delete(`/documentos/${id}`)
      fetchDocs()
    } catch (err) {
      showToast(err.response?.data?.detail || "Error al eliminar")
    }
  }

  async function descargar(id) {
    try {
      // Pedimos el archivo como blob para poder crear una URL local
      // y disparar la descarga sin abrir una nueva pestaña
      // El responseType "blob" es necesario para que axios no intente
      // parsear como JSON el binario del archivo
      const res = await api.get(`/documentos/${id}/descargar`, { responseType: "blob" })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement("a")
      a.href = url
      a.download = ""
      a.click()
      // Liberamos la URL temporal para evitar fugas de memoria
      URL.revokeObjectURL(url)
    } catch (err) {
      showToast("Error al descargar")
    }
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando documentos..." />

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Documentos DPD/ISO</h1>
        {esAdminTotal && (
          <select value={empresaFiltro} onChange={(e) => { setEmpresaFiltro(e.target.value); setPagina(1) }}>
            <option value="">Todas las empresas</option>
            {empresas.map((e) => (
              <option key={e.codigo_empresa} value={e.codigo_empresa}>{e.nombre}</option>
            ))}
          </select>
        )}
        <button className="btn-primary" onClick={() => setMostrarSubida(true)}>Subir documento</button>
      </div>

      {mostrarSubida && (
        // El clic en el overlay (fondo oscuro) cierra el modal;
        // stopPropagation en el contenido evita que se cierre al hacer
        // clic dentro del propio formulario
        <div className="modal-overlay" onClick={() => setMostrarSubida(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Subir documento</h3>
            <form onSubmit={subir}>
              <div className="campo">
                <label>Archivo</label>
                <input type="file" onChange={(e) => setArchivo(e.target.files[0])} required />
              </div>
              <div className="campo">
                <label>Tipo de documento</label>
                <select value={tipoDoc} onChange={(e) => setTipoDoc(e.target.value)}>
                  <option value="">Sin clasificar</option>
                  <option value="DPD">DPD</option>
                  <option value="ISO">ISO</option>
                </select>
              </div>
              <div className="modal-acciones">
                <button type="button" className="btn-secondary" onClick={() => setMostrarSubida(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Subir</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Renderizado condicional: cuando permisoDoc tiene valor,
          montamos el modal de permisos; al cerrarlo seteamos null
          y React desmonta el componente liberando sus recursos */}
      {permisoDoc && (
        <PermisosDoc doc={permisoDoc} onClose={() => setPermisoDoc(null)} onUpdated={fetchDocs} />
      )}

      <table className="tabla-admin">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Empresa</th>
            <th>Subido por</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {docs.length === 0 && <tr><td colSpan="6" className="sin-datos">No hay documentos</td></tr>}
          {ordenTipos.map((tipo) => {
            const docsGrupo = docsAgrupados[tipo]
            if (!docsGrupo || docsGrupo.length === 0) return null
            return (
              <Fragment key={tipo}>
                <tr className="grupo-header"><td colSpan="6"><strong>{tipo}</strong> ({docsGrupo.length})</td></tr>
                {docsGrupo.map((d) => (
                  <tr key={d.id_documento}>
                    <td>{d.nombre}</td>
                    <td>{d.tipo_documento || "—"}</td>
                    <td>{empresaMap[d.codigo_empresa] || (d.codigo_empresa ? `#${d.codigo_empresa}` : "—")}</td>
                    <td>#{d.usuario_subio}</td>
                    <td>{d.fecha}</td>
                    <td>
                      <div className="acciones">
                        <button className="btn-secundario btn-sm" onClick={() => descargar(d.id_documento)}>Descargar</button>
                        <button className="btn-secundario btn-sm" onClick={() => setPermisoDoc(d)}>Permisos</button>
                        <button className="btn-danger btn-sm" onClick={() => eliminar(d.id_documento)}>Eliminar</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </Fragment>
            )
          })}
        </tbody>
      </table>
      <Pagination pagina={pagina} totalPaginas={totalPaginas} onPaginaChange={setPagina} />
    </div>
  )
}
