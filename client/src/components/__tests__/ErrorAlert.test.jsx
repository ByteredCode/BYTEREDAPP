// Tests unitarios del componente ErrorAlert
// Verifica que muestra el mensaje de error y que no renderiza nada cuando no hay mensaje
import { render, screen } from '@testing-library/react'
import ErrorAlert from '../common/ErrorAlert'

describe('ErrorAlert', () => {
  it('renders error message', () => {
    // Con un mensaje, debe mostrarse en el DOM
    render(<ErrorAlert mensaje="Algo salió mal" />)
    expect(screen.getByText('Algo salió mal')).toBeInTheDocument()
  })

  it('renders nothing when mensaje is null', () => {
    // Sin mensaje (null), el componente debe retornar null y no ocupar espacio en el DOM
    const { container } = render(<ErrorAlert mensaje={null} />)
    expect(container.firstChild).toBeNull()
  })
})
