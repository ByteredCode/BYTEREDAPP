// Tests unitarios del componente LoadingSpinner
// Verifica que muestra el mensaje por defecto y los mensajes personalizados
import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../common/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders default message', () => {
    // Sin props, debe mostrar "Cargando..." por defecto
    render(<LoadingSpinner />)
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })

  it('renders custom message', () => {
    // Con la prop mensaje, debe mostrar el texto personalizado
    render(<LoadingSpinner mensaje="Obteniendo datos..." />)
    expect(screen.getByText('Obteniendo datos...')).toBeInTheDocument()
  })
})
