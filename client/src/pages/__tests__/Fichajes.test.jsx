import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Fichajes from '../Fichajes'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('Fichajes', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('shows empty state when no open fichaje', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: [] })
      if (url === '/fichajes/actual') return Promise.reject(new Error('No open'))
      return Promise.reject(new Error('Unknown'))
    })
    render(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('Sin fichajes')).toBeInTheDocument()
    })
  })

  it('shows registrar salida when there is an open fichaje', async () => {
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: [abierto] })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('Registrar salida')).toBeInTheDocument()
    })
  })

  it('displays fichaje history in table', async () => {
    const api = (await import('../../api/axios')).default
    const fichajes = [
      { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z', hora_salida: '2025-01-01T17:00:00Z' },
    ]
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: fichajes })
      if (url === '/fichajes/actual') return Promise.reject(new Error('No open'))
      return Promise.reject(new Error('Unknown'))
    })
    render(<Fichajes />)
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('calls salida API on button click', async () => {
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: [abierto] })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    api.post.mockResolvedValueOnce({})
    render(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Registrar salida')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Registrar salida'))
    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/fichajes/salida'))
  })

  it('shows alert on salida API error', async () => {
    const api = (await import('../../api/axios')).default
    const abierto = { id_fichaje: 1, hora_entrada: '2025-01-01T08:00:00Z' }
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.resolve({ data: [abierto] })
      if (url === '/fichajes/actual') return Promise.resolve({ data: abierto })
      return Promise.reject(new Error('Unknown'))
    })
    api.post.mockRejectedValueOnce({ response: { data: { detail: 'Error al fichar' } } })
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {})
    render(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Registrar salida')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Registrar salida'))
    await waitFor(() => expect(alertMock).toHaveBeenCalled())
    alertMock.mockRestore()
  })

  it('handles failed fichajes fetch gracefully', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/fichajes') return Promise.reject(new Error('DB error'))
      if (url === '/fichajes/actual') return Promise.resolve({ data: null })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Fichajes />)
    await waitFor(() => expect(screen.getByText('Sin fichajes')).toBeInTheDocument())
  })
})
