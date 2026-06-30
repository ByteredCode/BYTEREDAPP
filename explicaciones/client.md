# Explicación del frontend React

## package.json — Dependencias

```json
{
  "dependencies": {
    "axios": "^1.18.1",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "react-router-dom": "^7.18.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^6.0.1",
    "vite": "^8.0.12"
  }
}
```

### Dependencias de producción

- **react**: Librería principal para construir interfaces basadas en componentes
- **react-dom**: Puente entre React y el DOM del navegador
- **react-router-dom**: Enrutador para SPA (Single Page Application). Sin recargar la página, cambia entre componentes según la URL
- **axios**: Cliente HTTP con interceptores. Mejor que fetch() porque:
  - Soporta interceptores (para añadir JWT automáticamente)
  - Transforma errores HTTP en excepciones

### Dependencias de desarrollo

- **vite**: Bundler (empaquetador). En desarrollo sirve archivos con HMR (Hot Module Replacement), en producción genera archivos optimizados
- **@vitejs/plugin-react**: Plugin de Vite para React, añade soporte para JSX y Fast Refresh

---

## main.jsx — Punto de entrada

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

**createRoot**: React 18+ usa `createRoot` en lugar de `ReactDOM.render`. Monta la aplicación en el elemento HTML con id `root`.

**StrictMode**: Renderiza los componentes dos veces en desarrollo para detectar efectos secundarios. No afecta a producción.

---

## index.css — Estilos base

```css
body {
  margin: 0;
  font-family: system-ui, sans-serif;
}
```

Resetea el margen por defecto del body y usa la fuente del sistema. `system-ui` es un valor especial que usa la fuente nativa del sistema operativo (Segoe UI en Windows, San Francisco en macOS).

---

## api/axios.js — Cliente HTTP

```jsx
const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
})
```

Crea una **instancia** de axios con configuración base. Todas las peticiones usarán esta URL base y estos headers.

### Interceptor de request

```jsx
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

Se ejecuta **antes** de cada petición. Lee el token de localStorage y lo añade al header Authorization. Así no hay que escribir `Authorization: Bearer ...` en cada llamada.

### Interceptor de response

```jsx
api.interceptors.response.use(
  (res) => res,  // Si la respuesta es correcta, la pasa
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)
```

Se ejecuta **después** de cada respuesta. Si el servidor devuelve 401 (no autorizado), significa que el token expiró o es inválido. Borra los tokens y redirige al login. **Nota:** Esto no implementa refresh automático aún — es una funcionalidad pendiente.

---

## context/AuthContext.jsx — Estado global

```jsx
const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      api.get("/auth/me")
        .then((res) => setUsuario(res.data))
        .catch(() => { /* borrar tokens */ })
        .finally(() => setCargando(false))
    } else {
      setCargando(false)
    }
  }, [])

  const login = async (correo, contrasena) => {
    const res = await api.post("/auth/login", { correo, contrasena })
    localStorage.setItem("access_token", res.data.access_token)
    localStorage.setItem("refresh_token", res.data.refresh_token)
    const me = await api.get("/auth/me")
    setUsuario(me.data)
    return me.data
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
```

### ¿Qué es un Context?

Context es el mecanismo de React para compartir estado global sin pasarlo por props de componente en componente. Cualquier componente hijo de `AuthProvider` puede usar `useAuth()` y obtener `usuario`, `login`, `logout`.

### Flujo al cargar la app

```jsx
useEffect(() => { ... }, [])
```

El `useEffect` se ejecuta **una vez** al montar el componente. Comprueba si hay un token en localStorage. Si existe, llama a `/auth/me` para obtener los datos del usuario. Mientras carga, `cargando` es `true` (útil para mostrar un spinner).

### login()

1. POST a `/auth/login` con credenciales
2. Guarda los tokens en localStorage
3. Obtiene los datos del usuario con `/auth/me`
4. Actualiza el estado global

### ¿Por qué localStorage y no sessionStorage?

El token debe persistir aunque se cierre la pestaña del navegador. `sessionStorage` se borra al cerrar la pestaña. `localStorage` persiste hasta que se borre explícitamente.

---

## components/ProtectedRoute.jsx — Guardia de rutas

```jsx
export default function ProtectedRoute({ children }) {
  const { usuario, cargando } = useAuth()

  if (cargando) return <p>Cargando...</p>
  if (!usuario) return <Navigate to="/login" replace />

  return children
}
```

Es un **componente guardia** que envuelve rutas protegidas. Mientras se verifica el token, muestra "Cargando...". Si no hay usuario autenticado, redirige a `/login`.

`<Navigate to="/login" replace />`:
- **Navigate**: Componente de react-router-dom que redirige sin recargar
- **replace**: Reemplaza la entrada actual del historial (no se puede volver atrás con el botón de navegación)

---

## components/Layout.jsx — Layout base

```jsx
export default function Layout() {
  return (
    <div>
      <Outlet />
    </div>
  )
}
```

**Outlet** es un placeholder de react-router-dom. Donde se coloque `Outlet`, se renderizará el contenido de la ruta hija. Por ahora es básico (solo un `<div>`), pero aquí se añadirán headers, menús de navegación, etc.

---

## pages/Register.jsx — Registro de usuario

```jsx
export default function Register() {
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [nombre, setNombre] = useState("")
  const [codigoEmpresa, setCodigoEmpresa] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post("/auth/register", {
        correo, contrasena, nombre,
        codigo_empresa: Number(codigoEmpresa),
      })
      navigate("/login")
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrarse")
    }
  }
```

### Manejo de errores

```jsx
setError(err.response?.data?.detail || "Error al registrarse")
```

El operador `?.` (optional chaining) evita errores si `err.response` es undefined. Si el servidor devuelve un error con `detail` (el formato de FastAPI), se muestra ese mensaje. Si no, un mensaje genérico.

---

## pages/Login.jsx — Inicio de sesión

```jsx
export default function Login() {
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(correo, contrasena)
      navigate("/dashboard")
    } catch {
      setError("Credenciales incorrectas")
    }
  }
```

Usa `login` del AuthContext (que hace login + fetch de /me). Si funciona, redirige a `/dashboard`. Si falla, muestra error.

---

## pages/Dashboard.jsx — Panel principal

```jsx
export default function Dashboard() {
  const { usuario, logout } = useAuth()

  return (
    <div>
      <h1>Panel de control</h1>
      <p>Bienvenido, {usuario?.nombre}</p>
      <p>Rol: {usuario?.rol}</p>
      <p>Empresa: {usuario?.codigo_empresa}</p>
      <button onClick={logout}>Cerrar sesion</button>
    </div>
  )
}
```

**Dashboard mínimo de prueba.** Muestra datos del usuario autenticado y un botón para cerrar sesión. Cuando los módulos estén implementados, aquí irán los enlaces a cada módulo.

---

## App.jsx — Configuración de rutas

```jsx
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<Layout />}>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Route>
          <Route path="*" element={<Login />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
```

### Árbol de componentes

```
BrowserRouter
  └── AuthProvider
        └── Routes
              ├── /login → Login
              ├── /register → Register
              ├── (Layout)
              │     └── /dashboard → ProtectedRoute → Dashboard
              └── * → Login (catch-all)
```

### ¿Por qué Layout como ruta?

```jsx
<Route element={<Layout />}>
  <Route path="/dashboard" element={...} />
</Route>
```

Layout no tiene `path`, solo `element`. Esto significa que Layout se renderiza siempre, y dentro de él, el `Outlet` muestra el contenido de la ruta hija. Más adelante, Layout contendrá el menú de navegación, el header, etc., y todas las rutas protegidas se anidarán dentro.

---

## Resumen del flujo completo

```
1. USUARIO visita /register
   ↓
2. Register.jsx muestra formulario
   ↓
3. Usuario rellena → Submit
   ↓
4. api.post("/auth/register") → servidor
   ↓
5. Si OK → redirige a /login
   ↓
6. Login.jsx muestra formulario
   ↓
7. Usuario introduce credenciales → Submit
   ↓
8. AuthContext.login() → api.post("/auth/login")
   ↓
9. Guarda tokens en localStorage
   ↓
10. api.get("/auth/me") → obtiene datos del usuario
    ↓
11. AuthContext.setUsuario(data) → estado global actualizado
    ↓
12. Redirige a /dashboard
    ↓
13. Dashboard.jsx muestra datos del usuario
    ↓
14. Usuario hace clic en "Cerrar sesión"
    ↓
15. AuthContext.logout() → borra tokens y estado
```
