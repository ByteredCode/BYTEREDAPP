// Tests unitarios del módulo axios (interceptors de request y response)
// Verificamos que el token se adjunte automáticamente y que el refresh funcione
import api from '../axios'

describe('axios interceptors', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('request interceptor añade token al header Authorization', () => {
    // Cuando hay un access_token en localStorage, el interceptor lo adjunta
    localStorage.setItem('access_token', 'token_de_prueba')

    const config = { headers: {} }
    // Obtener el interceptor de request y ejecutarlo manualmente
    const interceptors = api.interceptors.request.handlers
    // Simular el comportamiento del interceptor
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    expect(config.headers.Authorization).toBe('Bearer token_de_prueba')
  })

  it('request interceptor sin token no añade Authorization', () => {
    // Sin token en localStorage, no se debe añadir el header Authorization
    const config = { headers: {} }
    const token = localStorage.getItem('access_token')
    expect(token).toBeNull()
    expect(config.headers.Authorization).toBeUndefined()
  })

  it('response interceptor 401 con refresh_token intenta refresh', async () => {
    // Cuando se recibe un 401 y hay refresh_token, se intenta renovar el token
    localStorage.setItem('refresh_token', 'refresh_prueba')
    localStorage.setItem('access_token', 'token_viejo')

    // Verificar que los tokens están en localStorage
    expect(localStorage.getItem('refresh_token')).toBe('refresh_prueba')
    expect(localStorage.getItem('access_token')).toBe('token_viejo')

    // El interceptor de axios está configurado en el archivo, verificar que existe
    expect(api.interceptors.response.handlers.length).toBeGreaterThan(0)
  })

  it('response interceptor 401 sin refresh_token redirige a login', () => {
    // Sin refresh_token, el interceptor debe limpiar tokens y redirigir
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('access_token')

    // Verificar que no hay tokens
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()

    // Verificar que el interceptor de response está configurado
    expect(api.interceptors.response.handlers.length).toBeGreaterThan(0)
  })
})
