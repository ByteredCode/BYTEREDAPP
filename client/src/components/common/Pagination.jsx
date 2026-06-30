export default function Pagination({ pagina, totalPaginas, total, onCambiarPagina }) {
  if (totalPaginas <= 1) return null

  return (
    <div className="pagination">
      <button disabled={pagina <= 1} onClick={() => onCambiarPagina(pagina - 1)}>Anterior</button>
      <span>Página {pagina} de {totalPaginas} ({total} registros)</span>
      <button disabled={pagina >= totalPaginas} onClick={() => onCambiarPagina(pagina + 1)}>Siguiente</button>
    </div>
  )
}
