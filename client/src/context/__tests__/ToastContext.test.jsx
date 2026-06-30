// Tests unitarios del contexto de notificaciones (ToastProvider)
// Verificamos que los toasts aparecen y desaparecen automáticamente tras 4 segundos
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ToastProvider, useToast } from '../ToastContext'

function TestComponent() {
  const { showToast } = useToast()
  return <button onClick={() => showToast('Mensaje de error', 'error')}>Mostrar</button>
}

describe('ToastContext', () => {
  beforeEach(() => { vi.useFakeTimers() })
  afterEach(() => { vi.useRealTimers() })

  it('shows and hides toast', () => {
    // Al pulsar el botón aparece el toast; tras 4 segundos debe desaparecer automáticamente
    render(<ToastProvider><TestComponent /></ToastProvider>)
    fireEvent.click(screen.getByText('Mostrar'))
    expect(screen.getByText('Mensaje de error')).toBeInTheDocument()
    act(() => { vi.advanceTimersByTime(4000) })
    expect(screen.queryByText('Mensaje de error')).not.toBeInTheDocument()
  })
})
