import { render, screen } from '@testing-library/react'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders default message', () => {
    render(<LoadingSpinner />)
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })

  it('renders custom message', () => {
    render(<LoadingSpinner mensaje="Obteniendo datos..." />)
    expect(screen.getByText('Obteniendo datos...')).toBeInTheDocument()
  })
})
