import { createContext, useCallback, useContext, useState } from "react"
// useCallback evita que showToast se re-cree en cada render, previniendo re-renderizados innecesarios de los hijos

// Iniciamos con null en vez de un objeto vacio para que useToast lance error si alguien lo usa fuera del Provider
const ToastContext = createContext(null)

// Variable fuera del estado de React: necesitamos IDs secuenciales unicos que persistan entre renders sin causar re-renderizados
let toastId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  // Pasamos el updater funcional a setToasts (prev => ...) para evitar depender del estado actual y posibles closures obsoletos
  const showToast = useCallback((mensaje, tipo = "error") => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, mensaje, tipo }])
    // Eliminamos la notificacion tras 4 segundos para que no se acumulen en pantalla
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/*
        Renderizamos el contenedor de toasts DENTRO del Provider para que los estilos
        y la posicion fija esten disponibles globalmente sin tener que montarlo en cada pagina
      */}
      <div className="toast-container">
        {toasts.map((t) => (
          // La key unica (id) evita que React confunda notificaciones al reordenarse o eliminarse
          <div key={t.id} className={`toast toast-${t.tipo}`}>
            {t.mensaje}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

// Hook de acceso directo: cualquier componente importa useToast() sin saber que internamente usa useContext
export function useToast() {
  return useContext(ToastContext)
}
