// Tests unitarios del formulario público de tickets (NuevoTicket)
// Verificamos renderizado, envío, estados de carga/éxito/error y reseteo del formulario
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import NuevoTicket from '../NuevoTicket'

vi.mock('../../../api/axios', () => ({
  default: { post: vi.fn() }
}))

describe('NuevoTicket', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders ticket form fields', () => {
    // El formulario debe mostrar todos los campos necesarios para crear un ticket
    render(<NuevoTicket />)
    expect(screen.getByText('Enviar ticket de soporte')).toBeInTheDocument()
    expect(screen.getByText('Nombre (opcional)')).toBeInTheDocument()
    expect(screen.getByText('Correo electrónico (opcional)')).toBeInTheDocument()
    expect(screen.getByText('Asunto')).toBeInTheDocument()
    expect(screen.getByText('Importancia')).toBeInTheDocument()
    expect(screen.getByText('Código de empresa')).toBeInTheDocument()
    expect(screen.getByText('Mensaje')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Enviar ticket' })).toBeInTheDocument()
  })

  it('submits form data to API', async () => {
    // Al completar el formulario y enviar, se debe llamar al endpoint POST /tickets
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[2], { target: { value: 'Asunto test' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje test' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalled()
    })
  })

  it('shows success message after submission', async () => {
    // Tras un envío exitoso, debe mostrarse la pantalla de confirmación "Ticket enviado"
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[2], { target: { value: 'Asunto' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
    await waitFor(() => {
      expect(screen.getByText('Ticket enviado')).toBeInTheDocument()
    })
  })

  it('shows error on API failure', async () => {
    // Si la API devuelve un error, debe mostrarse el mensaje de error en el formulario
    const api = (await import('../../../api/axios')).default
    api.post.mockRejectedValueOnce({
      response: { data: { detail: 'Error de conexión' } }
    })
    render(<NuevoTicket />)
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[2], { target: { value: 'Asunto' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
    await waitFor(() => {
      expect(screen.getByText('Error de conexión')).toBeInTheDocument()
    })
  })

  it('resets form after clicking Enviar otro', async () => {
    // Tras enviar, el botón "Enviar otro" debe resetear el formulario al estado inicial
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    render(<NuevoTicket />)
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[2], { target: { value: 'Asunto' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
    await waitFor(() => expect(screen.getByText('Enviar otro')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Enviar otro'))
    await waitFor(() => expect(screen.getByText('Enviar ticket de soporte')).toBeInTheDocument())
  })

  it('shows loading state while submitting', async () => {
    // Mientras se envía la petición, el botón debe mostrar "Enviando..." (estado de carga)
    const api = (await import('../../../api/axios')).default
    let resolvePromise
    api.post.mockReturnValueOnce(new Promise((resolve) => { resolvePromise = resolve }))
    render(<NuevoTicket />)
    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[2], { target: { value: 'Asunto' } })
    fireEvent.change(inputs[3], { target: { value: 'Mensaje' } })
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar ticket' }))
    expect(screen.getByText('Enviando...')).toBeInTheDocument()
    resolvePromise({})
    await waitFor(() => expect(screen.getByText('Enviar otro')).toBeInTheDocument())
  })
})
