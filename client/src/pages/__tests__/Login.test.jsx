import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import Login from '../Login'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

describe('Login', () => {
  const mockLogin = vi.fn()

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <AuthContext.Provider value={{ usuario: null, cargando: false, login: mockLogin, logout: vi.fn() }}>
          <Login />
        </AuthContext.Provider>
      </BrowserRouter>
    )
  }

  beforeEach(() => { vi.clearAllMocks() })

  it('renders email and password inputs', () => {
    renderLogin()
    expect(screen.getByPlaceholderText('Correo electrónico')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('submit button calls login function', async () => {
    mockLogin.mockResolvedValueOnce({ nombre: 'Juan' })
    renderLogin()
    fireEvent.change(screen.getByPlaceholderText('Correo electrónico'), { target: { value: 'a@a.com' } })
    fireEvent.change(screen.getByPlaceholderText('Contraseña'), { target: { value: 'pass' } })
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('a@a.com', 'pass')
    })
  })

  it('shows error on failed login', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Error'))
    renderLogin()
    fireEvent.change(screen.getByPlaceholderText('Correo electrónico'), { target: { value: 'a@a.com' } })
    fireEvent.change(screen.getByPlaceholderText('Contraseña'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    await waitFor(() => {
      expect(screen.getByText('Credenciales incorrectas')).toBeInTheDocument()
    })
  })

  it('redirects to dashboard on success', async () => {
    mockLogin.mockResolvedValueOnce({ nombre: 'Juan' })
    renderLogin()
    fireEvent.change(screen.getByPlaceholderText('Correo electrónico'), { target: { value: 'a@a.com' } })
    fireEvent.change(screen.getByPlaceholderText('Contraseña'), { target: { value: 'pass' } })
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
    })
  })
})
