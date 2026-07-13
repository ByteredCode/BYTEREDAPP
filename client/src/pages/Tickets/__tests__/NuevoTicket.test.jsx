// Tests unitarios del formulario público de tickets (NuevoTicket)
// Verificamos renderizado, envío, estados de carga/éxito/error y reseteo del formulario
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import NuevoTicket from '../NuevoTicket'

const mockGet = vi.fn()
const mockPost = vi.fn()

vi.mock('../../../api/axios', () => ({
  default: { get: (...args) => mockGet(...args), post: (...args) => mockPost(...args) }
}))

vi.mock('../../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ usuario: null })
}))

describe('NuevoTicket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGet.mockResolvedValue({ data: [{ codigo_empresa: 1, nombre: 'TestCorp' }] })
  })

  const fillAndSubmit = async () => {
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[1], { target: { value: 'test@test.com' } })
    fireEvent.change(inputs[2], { target: { value: 'Asunto test' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje test' } })
    const selects = screen.getAllByRole('combobox')
    fireEvent.change(selects[0], { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
  }

  it('renders ticket form fields', async () => {
    render(<NuevoTicket />)
    expect(await screen.findByText('Enviar ticket de soporte')).toBeInTheDocument()
    expect(screen.getByText('Nombre (opcional)')).toBeInTheDocument()
    expect(screen.getByText('Correo electrónico')).toBeInTheDocument()
    expect(screen.getByText('Asunto')).toBeInTheDocument()
    expect(screen.getByText('Empresa')).toBeInTheDocument()
    expect(screen.getByText('Mensaje')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Enviar ticket' })).toBeInTheDocument()
  })

  it('submits form data to API', async () => {
    mockPost.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    await screen.findByText('Enviar ticket de soporte')
    await fillAndSubmit()
    await waitFor(() => {
      expect(mockPost).toHaveBeenCalled()
    })
  })

  it('shows success message after submission', async () => {
    mockPost.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    await screen.findByText('Enviar ticket de soporte')
    await fillAndSubmit()
    await waitFor(() => {
      expect(screen.getByText('Ticket enviado')).toBeInTheDocument()
    })
  })

  it('shows error on API failure', async () => {
    mockPost.mockRejectedValueOnce({
      response: { data: { detail: 'Error de conexión' } }
    })
    render(<NuevoTicket />)
    await screen.findByText('Enviar ticket de soporte')
    await fillAndSubmit()
    await waitFor(() => {
      expect(screen.getByText('Error de conexión')).toBeInTheDocument()
    })
  })

  it('resets form after clicking Enviar otro', async () => {
    mockPost.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    await screen.findByText('Enviar ticket de soporte')
    await fillAndSubmit()
    await waitFor(() => expect(screen.getByText('Enviar otro')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Enviar otro'))
    await waitFor(() => expect(screen.getByText('Enviar ticket de soporte')).toBeInTheDocument())
  })

  it('shows loading state while submitting', async () => {
    let resolvePromise
    mockPost.mockReturnValueOnce(new Promise((resolve) => { resolvePromise = resolve }))
    render(<NuevoTicket />)
    await screen.findByText('Enviar ticket de soporte')
    await fillAndSubmit()
    expect(screen.getByText('Enviando...')).toBeInTheDocument()
    resolvePromise({})
    await waitFor(() => expect(screen.getByText('Enviar otro')).toBeInTheDocument())
  })
})
