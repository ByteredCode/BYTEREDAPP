import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'  // Estilos globales de la aplicacion
import App from './App.jsx'

// Punto de entrada: monta la aplicacion React en el elemento <div id="root">
// StrictMode activa verificaciones en desarrollo (renderizado doble, efectos, etc.)
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
