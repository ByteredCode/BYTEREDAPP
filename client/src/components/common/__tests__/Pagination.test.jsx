import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from '../Pagination'

describe('Pagination', () => {
  it('renders nothing when totalPaginas <= 1', () => {
    const { container } = render(
      <Pagination pagina={1} totalPaginas={1} total={5} onCambiarPagina={vi.fn()} />
    )
    expect(container.innerHTML).toBe('')
  })

  it('disables Anterior on first page', () => {
    render(
      <Pagination pagina={1} totalPaginas={3} total={10} onCambiarPagina={vi.fn()} />
    )
    expect(screen.getByText('Anterior')).toBeDisabled()
    expect(screen.getByText('Siguiente')).not.toBeDisabled()
  })

  it('disables Siguiente on last page', () => {
    render(
      <Pagination pagina={3} totalPaginas={3} total={10} onCambiarPagina={vi.fn()} />
    )
    expect(screen.getByText('Siguiente')).toBeDisabled()
    expect(screen.getByText('Anterior')).not.toBeDisabled()
  })

  it('calls onCambiarPagina with previous page', () => {
    const onChange = vi.fn()
    render(
      <Pagination pagina={2} totalPaginas={3} total={10} onCambiarPagina={onChange} />
    )
    fireEvent.click(screen.getByText('Anterior'))
    expect(onChange).toHaveBeenCalledWith(1)
  })

  it('calls onCambiarPagina with next page', () => {
    const onChange = vi.fn()
    render(
      <Pagination pagina={2} totalPaginas={3} total={10} onCambiarPagina={onChange} />
    )
    fireEvent.click(screen.getByText('Siguiente'))
    expect(onChange).toHaveBeenCalledWith(3)
  })

  it('displays current page and total', () => {
    render(
      <Pagination pagina={2} totalPaginas={5} total={23} onCambiarPagina={vi.fn()} />
    )
    expect(screen.getByText(/Página 2 de 5/)).toBeInTheDocument()
    expect(screen.getByText(/23 registros/)).toBeInTheDocument()
  })
})
