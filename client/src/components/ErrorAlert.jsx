export default function ErrorAlert({ mensaje }) {
  if (!mensaje) return null
  return <div className="alert alert-error">{mensaje}</div>
}
