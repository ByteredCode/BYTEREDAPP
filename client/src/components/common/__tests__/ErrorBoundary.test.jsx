// Tests unitarios del componente ErrorBoundary
// Verificamos renderizado normal y captura de errores
import { render, screen } from '@testing-library/react'
import ErrorBoundary from '../ErrorBoundary'

// Componente que lanza error para provocar el ErrorBoundary
function ThrowError() {
  throw new Error('Error de prueba')
}

describe('ErrorBoundary', () => {
  // Silenciar el console.error que genera ErrorBoundary al capturar errores
  const originalError = console.error
  beforeEach(() => {
    console.error = vi.fn()
  })
  afterEach(() => {
    console.error = originalError
  })

  it('renderiza children sin error', () => {
    // Cuando no hay errores, ErrorBoundary renderiza sus children normalmente
    render(
      <ErrorBoundary>
        <div>Contenido normal</div>
      </ErrorBoundary>
    )
    expect(screen.getByText('Contenido normal')).toBeInTheDocument()
  })

  it('muestra UI de error al capturar excepción', () => {
    // Cuando un child lanza error, ErrorBoundary muestra la UI de fallback
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    expect(screen.getByText('Algo salió mal')).toBeInTheDocument()
    expect(screen.getByText(/Ha ocurrido un error inesperado/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Recargar página' })).toBeInTheDocument()
  })
})
