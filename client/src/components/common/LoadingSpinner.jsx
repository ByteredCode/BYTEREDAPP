// Componente mínimo y reutilizable: muestra un mensaje de carga mientras se espera una respuesta asíncrona
export default function LoadingSpinner({ mensaje = "Cargando..." }) {
  // El valor por defecto permite usarlo sin props, pero el mensaje es personalizable si se necesita
  return <p className="cargando">{mensaje}</p>
}
