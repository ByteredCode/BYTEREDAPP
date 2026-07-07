export default function Pagination({ pagina, totalPaginas, total, onCambiarPagina, onPaginaChange }) {
  const onChange = onCambiarPagina || onPaginaChange
  if (totalPaginas <= 1) return null

  return (
    <div className="pagination">
      <button disabled={pagina <= 1} onClick={() => onChange(pagina - 1)}>Anterior</button>
      <span>Página {pagina} de {totalPaginas}{total !== undefined ? ` (${total} registros)` : ""}</span>
      <button disabled={pagina >= totalPaginas} onClick={() => onChange(pagina + 1)}>Siguiente</button>
    </div>
  )
}
