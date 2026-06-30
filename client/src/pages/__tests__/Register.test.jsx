// Tests unitarios de la página de registro (Register)
// Verificamos renderizado de campos, validación y manejo de errores del backend
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Register from '../Register'

vi.mock('../../api/axios', () => ({
  default: { post: vi.fn() }
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

describe('Register', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderRegister = () => render(<BrowserRouter><Register /></BrowserRouter>)

  it('renders all form fields', () => {
    // El formulario de registro debe mostrar todos los campos requeridos
    renderRegister()
    expect(screen.getByPlaceholderText('Nombre completo')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Correo electrónico')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contraseña')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Código de empresa')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Registrarse' })).toBeInTheDocument()
  })

  it('validates required fields', () => {
    // Los campos obligatorios deben tener el atributo required del navegador
    renderRegister()
    const inputs = screen.getAllByRole('textbox')
    inputs.concat(screen.getAllByRole('spinbutton')).forEach((input) => {
      expect(input).toBeRequired()
    })
  })

  it('shows error for short password (mock API)', async () => {
    // El backend rechaza contraseñas cortas; el frontend debe mostrar el mensaje de error
    const api = (await import('../../api/axios')).default
    api.post.mockRejectedValueOnce({
      response: { data: { detail: 'La contraseña debe tener al menos 8 caracteres' } }
    })
    renderRegister()
    fireEvent.change(screen.getByPlaceholderText('Nombre completo'), { target: { value: 'Juan' } })
    fireEvent.change(screen.getByPlaceholderText('Correo electrónico'), { target: { value: 'a@a.com' } })
    fireEvent.change(screen.getByPlaceholderText('Contraseña'), { target: { value: '123' } })
    fireEvent.change(screen.getByPlaceholderText('Código de empresa'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Registrarse' }))
    await waitFor(() => {
      expect(screen.getByText('La contraseña debe tener al menos 8 caracteres')).toBeInTheDocument()
    })
  })

  it('shows error for weak password (no uppercase)', async () => {
    // El backend rechaza contraseñas sin mayúsculas; el frontend debe mostrar el error
    const api = (await import('../../api/axios')).default
    api.post.mockRejectedValueOnce({
      response: { data: { detail: 'La contraseña debe contener al menos una mayúscula' } }
    })
    renderRegister()
    fireEvent.change(screen.getByPlaceholderText('Nombre completo'), { target: { value: 'Juan' } })
    fireEvent.change(screen.getByPlaceholderText('Correo electrónico'), { target: { value: 'a@a.com' } })
    fireEvent.change(screen.getByPlaceholderText('Contraseña'), { target: { value: 'abcdefgh' } })
    fireEvent.change(screen.getByPlaceholderText('Código de empresa'), { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Registrarse' }))
    await waitFor(() => {
      expect(screen.getByText('La contraseña debe contener al menos una mayúscula')).toBeInTheDocument()
    })
  })
})
