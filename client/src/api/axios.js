import axios from "axios"

// Instancia de Axios con configuracion base para toda la app
const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
})

// Interceptor de request: inyecta el token JWT en cada peticion
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor de response: si el token expiro (401), redirige al login
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

export default api
