// Componente puro: solo renderiza algo si hay mensaje, evitando un div vacío en el DOM
export default function ErrorAlert({ mensaje }) {
  // Si no hay mensaje retornamos null para no contaminar el árbol de nodos con alertas invisibles
  if (!mensaje) return null
  return <div className="alert alert-error">{mensaje}</div>
}
