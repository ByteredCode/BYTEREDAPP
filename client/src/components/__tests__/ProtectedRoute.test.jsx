// Tests unitarios del guardia de autenticación (ProtectedRoute)
// Verifica que solo usuarios autenticados puedan ver el contenido protegido
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import ProtectedRoute from '../ProtectedRoute'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('ProtectedRoute', () => {
  const renderProtected = ({ usuario, cargando }) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando, login: vi.fn(), logout: vi.fn() }}>
          <ProtectedRoute>
            <div>Contenido protegido</div>
          </ProtectedRoute>
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('renders children when authenticated', () => {
    // Con usuario autenticado, debe mostrarse el contenido hijo
    renderProtected({ usuario: { nombre: 'Juan' }, cargando: false })
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    // Sin usuario, debe redirigir al login (Navigate to="/login")
    renderProtected({ usuario: null, cargando: false })
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('shows loading state', () => {
    // Mientras se verifica la sesión (cargando=true), debe mostrar un spinner/mensaje de carga
    renderProtected({ usuario: null, cargando: true })
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })
})
