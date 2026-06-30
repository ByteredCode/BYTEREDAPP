import { useState, useEffect, useCallback } from "react"
import api from "../api/axios"
import { useToast } from "../context/ToastContext"
import LoadingSpinner from "../components/common/LoadingSpinner"
import Pagination from "../components/common/Pagination"

export default function Fichajes() {
  const { showToast } = useToast()
  // fichajes: historial completo; abierto: fichaje activo (entrada sin salida); resumen: estadísticas agregadas
  const [fichajes, setFichajes] = useState([])
  const [abierto, setAbierto] = useState(null)
  const [resumen, setResumen] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [pagina, setPagina] = useState(1)
  const [totalPaginas, setTotalPaginas] = useState(1)

  const fetchData = useCallback(async () => {
    setCargando(true)
    try {
      const [resFichajes, resActual, resResumen] = await Promise.allSettled([
        api.get("/fichajes", { params: { skip: (pagina - 1) * 50, limit: 50 } }),
        api.get("/fichajes/actual"),
        api.get("/fichajes/resumen"),
      ])
      if (resFichajes.status === "fulfilled") {
        setFichajes(resFichajes.value.data.items)
        setTotalPaginas(Math.ceil(resFichajes.value.data.total / 50) || 1)
      }
      if (resActual.status === "fulfilled") setAbierto(resActual.value.data)
      else setAbierto(null)
      if (resResumen.status === "fulfilled") setResumen(resResumen.value.data)
    } catch { /* ignore */ }
    finally { setCargando(false) }
  }, [pagina])

  // Se ejecuta al montar el componente; la dependencia fetchData (memoizada) es estable.
  useEffect(() => { fetchData() }, [fetchData])

  // Se invoca al pulsar "Registrar salida"; el POST no lleva body porque el backend
  // identifica el fichaje abierto a través del JWT del usuario (sesión activa).
  async function ficharSalida() {
    try {
      await api.post("/fichajes/salida")
      // Tras registrar la salida se refrescan todos los datos para reflejar el cambio.
      fetchData()
    } catch (err) {
      // showToast muestra una notificación temporal sin bloquear la interacción,
      // a diferencia de alert() que requiere acción explícita del usuario.
      showToast(err.response?.data?.detail || err.message)
    }
  }

  // Se abre la URL en una pestaña nueva para que el navegador maneje la descarga
  // del CSV directamente, sin tener que procesar el blob ni crear un enlace temporal.
  function exportarCSV() {
    const url = api.defaults?.baseURL ? api.defaults.baseURL + "/fichajes/exportar" : "/fichajes/exportar"
    window.open(url, "_blank")
  }

  if (cargando) return <LoadingSpinner mensaje="Cargando fichajes..." />

  return (
    <div className="pagina-admin">
      <div className="pagina-admin-header">
        <h1>Fichajes</h1>
        {/* Si hay un fichaje abierto se muestra la hora de entrada y el botón de salida;
            si no hay, simplemente no se renderiza nada (sin placeholder). */}
        {abierto && (
          <div className="fichaje-abierto">
            {/* Se convierte la fecha ISO 8601 del backend al locale del navegador
                para que el usuario vea su hora local sin tener que hacer el cálculo mental. */}
            <span>Abierto desde: {new Date(abierto.hora_entrada).toLocaleTimeString()}</span>
            <button className="btn-danger" onClick={ficharSalida}>Registrar salida</button>
          </div>
        )}
      </div>

      {/* El resumen solo se renderiza cuando hay datos; así se evita mostrar
          ceros o valores vacíos mientras el servidor aún no ha respondido. */}
      {resumen && (
        <div className="stats-grid fichajes-resumen">
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_hoy}</span>
            <span className="stats-label">Horas hoy</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_semana}</span>
            <span className="stats-label">Horas esta semana</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.horas_mes}</span>
            <span className="stats-label">Horas este mes</span>
          </div>
          <div className="stats-card">
            <span className="stats-num">{resumen.total_fichajes}</span>
            <span className="stats-label">Total fichajes</span>
          </div>
        </div>
      )}

      <div className="pagina-admin-header">
        <button className="btn btn-sm" onClick={exportarCSV}>Exportar CSV</button>
      </div>

      <table className="tabla-admin">
        <thead>
          <tr>
            <th>#</th>
            <th>Entrada</th>
            <th>Salida</th>
            <th>Duración</th>
          </tr>
        </thead>
        <tbody>
          {fichajes.length === 0 && <tr><td colSpan="4" className="sin-datos">Sin fichajes</td></tr>}
          {fichajes.map((f) => {
            // Conversión de ISO 8601 (UTC) a objeto Date para formatear en locale local;
            // el backend almacena en UTC pero el usuario ve su propia zona horaria.
            const entrada = new Date(f.hora_entrada)
            // Si salida es null es que el fichaje sigue abierto; se evita crear un Date inválido.
            const salida = f.hora_salida ? new Date(f.hora_salida) : null
            // Diferencia en milisegundos convertida a minutos para legibilidad humana;
            // Math.round evita decimales que añadirían ruido visual.
            const duracion = salida ? Math.round((salida - entrada) / 60000) + " min" : "—"
            return (
              // id_fichaje como key única para que React optimice el re-renderizado de la fila.
              <tr key={f.id_fichaje}>
                <td>{f.id_fichaje}</td>
                <td>{entrada.toLocaleString()}</td>
                <td>{salida ? salida.toLocaleString() : "—"}</td>
                <td>{duracion}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <Pagination pagina={pagina} totalPaginas={totalPaginas} onPaginaChange={setPagina} />
    </div>
  )
}
