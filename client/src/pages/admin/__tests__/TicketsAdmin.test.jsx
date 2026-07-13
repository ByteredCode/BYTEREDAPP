import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import TicketsAdmin from '../TicketsAdmin'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), put: vi.fn() }
}))

vi.mock('../../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ usuario: { nombre: 'Admin', rol: 'admin_total' } })
}))

describe('TicketsAdmin', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderTickets = () => {
    return render(
      <ToastProvider>
        <TicketsAdmin />
      </ToastProvider>
    )
  }

  const mockTickets = [
    { id_reporte: 1, asunto: 'Problema login', nombre_contacto: 'Ana', correo_contacto: 'ana@test.com', nivel_importancia: 'Alta', estado: 'Pendiente', mensaje: 'No puedo entrar', fecha_reporte: '2026-06-01T10:00:00Z' },
    { id_reporte: 2, asunto: 'Error factura', nombre_contacto: 'Luis', nivel_importancia: 'Media', estado: 'Leido', mensaje: 'Factura incorrecta', fecha_reporte: '2026-06-02T12:00:00Z' },
  ]

  it('shows loading spinner initially', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderTickets()
    expect(screen.getByText('Cargando tickets...')).toBeInTheDocument()
  })

  it('shows empty state when no tickets', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderTickets()
    await waitFor(() => {
      expect(screen.getByText('No hay tickets')).toBeInTheDocument()
    })
  })

  it('renders ticket table with data', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockTickets, total: 2 } })
    renderTickets()
    await waitFor(() => {
      expect(screen.getByText('Problema login')).toBeInTheDocument()
      expect(screen.getByText('Error factura')).toBeInTheDocument()
      expect(screen.getByText('Ana')).toBeInTheDocument()
      expect(screen.getByText('Luis')).toBeInTheDocument()
    })
  })

  it('opens detail modal on Ver click', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockTickets, total: 2 } })
    renderTickets()
    await waitFor(() => expect(screen.getByText('Problema login')).toBeInTheDocument())
    fireEvent.click(screen.getAllByText('Ver')[0])
    await waitFor(() => {
      expect(screen.getByText('No puedo entrar')).toBeInTheDocument()
    })
  })

  it('changes ticket status in modal', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockTickets, total: 2 } })
    api.put.mockResolvedValueOnce({})
    renderTickets()
    await waitFor(() => expect(screen.getByText('Problema login')).toBeInTheDocument())
    fireEvent.click(screen.getAllByText('Ver')[0])
    await waitFor(() => expect(screen.getByText('No puedo entrar')).toBeInTheDocument())
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'Leido' } })
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/tickets/1/estado', expect.any(Object))
    })
  })

  it('closes modal via overlay click', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockTickets, total: 2 } })
    renderTickets()
    await waitFor(() => expect(screen.getByText('Problema login')).toBeInTheDocument())
    fireEvent.click(screen.getAllByText('Ver')[0])
    await waitFor(() => expect(screen.getByText('Ticket #1')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Cerrar'))
    await waitFor(() => {
      expect(screen.queryByText('Ticket #1')).not.toBeInTheDocument()
    })
  })
})
