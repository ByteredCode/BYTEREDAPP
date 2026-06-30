// Tests unitarios de la página de fichajes (control horario)
// Verificamos estados vacío, fichaje abierto, historial, botón de salida y manejo de errores
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Fichajes from '../Fichajes'
import { ToastProvider } from '../../context/ToastContext'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

function renderConToast(ui) {
  return render(<ToastProvider>{ui}</ToastProvider>)
}

describe('Fichajes', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('shows empty state when no open fichaje', async () => {
    // Sin fichajes en el historial debe mostrar el mensaje "Sin fichajes"
    const api = (await import('../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: { items: [], total: 0 } })
      if (url === '/fichajes/actual') return Promise.reject(new Error('No open'))
      return Promise.reject(new Error('Unknown'))
    })
    renderConToast(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('Sin fichajes')).toBeInTheDocument()
    })
  })

  it('shows registrar salida when there is an open fichaje', async () => {
    // Si hay un fichaje abierto (sin salida), debe mostrarse el botón "Registrar salida"
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: { items: [abierto], total: 1 } })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    renderConToast(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('Registrar salida')).toBeInTheDocument()
    })
  })

  it('displays fichaje history in table', async () => {
    // El historial de fichajes debe renderizarse en una tabla con los datos correctos
    const api = (await import('../../api/axios')).default
    const fichajes = [
      { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z', hora_salida: '2025-01-01T17:00:00Z' },
    ]
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: { items: fichajes, total: 1 } })
      if (url === '/fichajes/actual') return Promise.reject(new Error('No open'))
      return Promise.reject(new Error('Unknown'))
    })
    renderConToast(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('calls salida API on button click', async () => {
    // Al pulsar "Registrar salida", se debe llamar al endpoint POST /fichajes/salida
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: { items: [abierto], total: 1 } })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    api.post.mockResolvedValueOnce({})
    renderConToast(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Registrar salida')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Registrar salida'))
    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/fichajes/salida'))
  })

  it('shows toast on salida API error', async () => {
    // Si la API de salida falla, debe mostrarse un toast con el mensaje de error
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: { items: [abierto], total: 1 } })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    api.post.mockRejectedValueOnce({ response: { data: { detail: 'Error al fichar' } } })
    renderConToast(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Registrar salida')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Registrar salida'))
    await waitFor(() => {
      expect(screen.getByText('Error al fichar')).toBeInTheDocument()
    })
  })

  it('handles failed fichajes fetch gracefully', async () => {
    // Si falla la petición de fichajes, el componente no debe romperse (catch silencioso)
    const api = (await import('../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.reject(new Error('DB error'))
      if (url === '/fichajes/actual') return Promise.resolve({ data: { items: [], total: 0 } })
      return Promise.reject(new Error('Unknown'))
    })
    renderConToast(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Sin fichajes')).toBeInTheDocument())
  })
})
