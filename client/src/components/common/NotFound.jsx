import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="not-found">
      <h1>404</h1>
      <p>La página que buscas no existe.</p>
      <Link to="/dashboard" className="btn btn-primary">Volver al inicio</Link>
    </div>
  )
}
