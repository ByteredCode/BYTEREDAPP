import { render, screen, act, waitFor } from '@testing-library/react'
import { useContext } from 'react'
import { AuthContext, AuthProvider } from '../AuthContext'

vi.mock('../../api/axios', () => ({
  default: { post: vi.fn(), get: vi.fn() }
}))

function TestConsumer() {
  const { usuario, cargando, login, logout } = useContext(AuthContext)
  return (
    <div>
      <span data-testid="usuario">{usuario ? usuario.nombre : 'null'}</span>
      <span data-testid="cargando">{cargando ? 'true' : 'false'}</span>
      <button data-testid="btn-login" onClick={() => login('a@a.com', 'pass')}>login</button>
      <button data-testid="btn-logout" onClick={logout}>logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('provides default null user and loading false', async () => {
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    await waitFor(() => {
      expect(screen.getByTestId('cargando').textContent).toBe('false')
    })
    expect(screen.getByTestId('usuario').textContent).toBe('null')
  })

  it('login stores tokens and sets user', async () => {
    const api = (await import('../../api/axios')).default
    api.post.mockResolvedValueOnce({ data: { access_token: 'acc-test', refresh_token: 'ref-test' } })
    api.get.mockResolvedValueOnce({ data: { nombre: 'Juan', rol: 'user' } })
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    await waitFor(() => expect(screen.getByTestId('cargando').textContent).toBe('false'))
    await act(async () => {
      screen.getByTestId('btn-login').click()
    })
    expect(localStorage.getItem('access_token')).toBe('acc-test')
    expect(localStorage.getItem('refresh_token')).toBe('ref-test')
    await waitFor(() => {
      expect(screen.getByTestId('usuario').textContent).toBe('Juan')
    })
  })

  it('logout clears tokens and sets user null', async () => {
    const api = (await import('../../api/axios')).default
    localStorage.setItem('access_token', 'acc-test')
    localStorage.setItem('refresh_token', 'ref-test')
    api.get.mockResolvedValueOnce({ data: { nombre: 'Juan' } })
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    await waitFor(() => {
      expect(screen.getByTestId('usuario').textContent).toBe('Juan')
    })
    api.post.mockResolvedValueOnce({})
    await act(async () => {
      screen.getByTestId('btn-logout').click()
    })
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(screen.getByTestId('usuario').textContent).toBe('null')
  })
})
