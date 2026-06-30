import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
})

let refrescando = false
let colaPeticiones = []

function procesarCola(error, token = null) {
  colaPeticiones.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  colaPeticiones = []
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const peticionOriginal = error.config
    if (error.response?.status === 401 && !peticionOriginal._retry) {
      if (refrescando) {
        return new Promise((resolve, reject) => {
          colaPeticiones.push({ resolve, reject })
        }).then((token) => {
          peticionOriginal.headers.Authorization = `Bearer ${token}`
          return api(peticionOriginal)
        })
      }
      peticionOriginal._retry = true
      refrescando = true
      const refreshToken = localStorage.getItem("refresh_token")
      if (!refreshToken) {
        procesarCola(error)
        refrescando = false
        localStorage.removeItem("access_token")
        window.location.href = "/login"
        return Promise.reject(error)
      }
      try {
        const res = await api.post("/auth/refresh", {
          refresh_token: refreshToken,
        })
        const nuevoAccess = res.data.access_token
        localStorage.setItem("access_token", nuevoAccess)
        procesarCola(null, nuevoAccess)
        refrescando = false
        peticionOriginal.headers.Authorization = `Bearer ${nuevoAccess}`
        return api(peticionOriginal)
      } catch {
        procesarCola(error)
        refrescando = false
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        window.location.href = "/login"
        return Promise.reject(error)
      }
    }
    return Promise.reject(error)
  }
)

export default api
