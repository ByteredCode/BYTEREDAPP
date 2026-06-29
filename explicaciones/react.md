# React — Guía completa para entender el frontend

## 1. ¿Qué es React?

React es una **librería** (no un framework) para construir interfaces de usuario. Fue creada por Jordan Walke en Facebook en 2011 y se hizo pública en 2013.

**Librería vs Framework:**

| | Librería | Framework |
|---|---|---|
| Control | Tú llamas a la librería | El framework te llama a ti |
| Flexibilidad | Alta (eliges herramientas) | Baja (todo integrado) |
| Ejemplo | React + React Router + Axios | Angular (todo incluido) |

React solo se encarga de la **capa de vista** (V en MVC). Para rutas necesitas React Router, para peticiones HTTP necesitas Axios o fetch(), etc.

### Filosofía de React

React se basa en una idea fundamental: **las vistas son funciones del estado**.

```
Vista = f(estado)
```

Dado el mismo estado, React siempre renderiza la misma vista. Cuando el estado cambia, React **vuelve a renderizar** la vista completa. No hay manipulación manual del DOM.

---

## 2. Virtual DOM

### El problema del DOM real

Manipular el DOM (Document Object Model) es **lento**. Cada vez que añades, modificas o eliminas un elemento del DOM, el navegador tiene que:

1. Recalcular estilos (CSS)
2. Recalcular layout (posición y tamaño)
3. Repintar (píxeles en pantalla)
4. Componer capas

Si tu app hace 100 cambios al DOM, el navegador hace 100 ciclos completos.

### Cómo resuelve React el problema

React mantiene una **copia virtual del DOM en memoria** (un objeto JavaScript ligero). Cuando el estado cambia:

1. React construye un **nuevo Virtual DOM** con los cambios
2. Compara el Virtual DOM anterior con el nuevo (**diffing**)
3. Calcula el **conjunto mínimo de cambios** necesarios en el DOM real
4. Aplica solo esos cambios (**reconciliation**)

```
Estado cambia → Nuevo Virtual DOM → Diff → Parches mínimos → DOM real
```

Esto es mucho más rápido porque:
- Comparar objetos JavaScript en memoria es barato
- Las operaciones reales del DOM se minimizan
- Los cambios se agrupan y aplican en lotes

### Algoritmo de diffing

React usa **heurísticas** (no una comparación O(n³) ingenua):

1. **Elementos de distinto tipo** → destruye el viejo, crea el nuevo (ej: pasar de `<div>` a `<span>`)
2. **Elementos del mismo tipo** → actualiza solo los atributos que cambiaron
3. **Componentes del mismo tipo** → actualiza las props, ejecuta useEffect, etc.
4. **Listas con key** → usa la `key` para identificar qué elementos se movieron, añadieron o eliminaron

**Importancia de las keys en listas:**

```jsx
// ❌ Sin key: React no sabe qué cambió
items.map(item => <li>{item.text}</li>)

// ✅ Con key: React sabe exactamente qué cambió
items.map(item => <li key={item.id}>{item.text}</li>)
```

Sin `key`, React podría reordenar o recrear elementos incorrectamente, causando bugs sutiles.

---

## 3. JSX

JSX es una **extensión de sintaxis** para JavaScript que parece HTML pero se compila a `React.createElement()`.

```jsx
// JSX
const element = <h1 className="titulo">Hola</h1>

// Se compila a:
const element = React.createElement('h1', { className: 'titulo' }, 'Hola')
```

### Reglas de JSX

1. **Un solo elemento raíz** — no puedes devolver dos hermanos sin un wrapper

```jsx
// ❌ Incorrecto
return (
  <h1>Título</h1>
  <p>Párrafo</p>
)

// ✅ Correcto (Fragment)
return (
  <>
    <h1>Título</h1>
    <p>Párrafo</p>
  </>
)
```

2. **Cierre de todas las etiquetas** — incluso las que en HTML son autocerradas

```jsx
// HTML: <br>
// JSX: <br />

// HTML: <input>
// JSX: <input />
```

3. **Atributos en camelCase** — `class` → `className`, `onclick` → `onClick`, `tabindex` → `tabIndex`

4. **Expresiones con {}** — no con {{}} ni con "${}"

```jsx
const nombre = "Ana"
return <h1>Hola, {nombre}</h1>  // ✅ Correcto
```

### ¿Por qué JSX y no plantillas?

A diferencia de Angular (que usa `{{ }}`) o Vue (que usa `{{ }}` y directivas), JSX no es un sistema de plantillas. Es JavaScript. Puedes usar `if`, `for`, `map`, ternarios, etc. directamente:

```jsx
return (
  <ul>
    {usuarios
      .filter(u => u.activo)
      .map(u => <li key={u.id}>{u.nombre}</li>)
    }
  </ul>
)
```

---

## 4. Componentes

Un componente es una **función que recibe props y devuelve JSX**.

### Componente funcional (el estándar actual)

```jsx
function Saludo({ nombre, edad }) {
  return <p>Hola, {nombre}. Tienes {edad} años.</p>
}
```

### Componente de clase (legado, no se usa en proyectos nuevos)

```jsx
class Saludo extends React.Component {
  render() {
    return <p>Hola, {this.props.nombre}</p>
  }
}
```

### Composición vs Herencia

**React favorece la composición sobre la herencia.**

- **Herencia** (Java/C++): una clase extiende otra para reutilizar comportamiento
- **Composición** (React): componentes pequeños se combinan para formar componentes más grandes

```jsx
// Composición
function Panel({ titulo, children }) {
  return (
    <div className="panel">
      <h2>{titulo}</h2>
      {children}
    </div>
  )
}

// Uso
<Panel titulo="Usuarios">
  <Usuario nombre="Ana" />
  <Usuario nombre="Luis" />
</Panel>
```

`children` es una **prop especial** que contiene todo lo que se ponga entre las etiquetas de apertura y cierre del componente.

### Nombrado de componentes

Los componentes **siempre empiezan con mayúscula**. Las etiquetas en minúscula (`<div>`, `<span>`) se tratan como elementos HTML nativos. Las etiquetas en mayúscula (`<Usuario>`, `<Panel>`) se tratan como componentes React.

---

## 5. Props

Las **props** (properties) son los argumentos que recibe un componente. Son **inmutables** (no se pueden modificar dentro del componente).

### Flujo unidireccional (one-way data binding)

Los datos fluen de **padre a hijo**, nunca al revés.

```
App → Panel → Usuario
           → Boton
```

Si un hijo necesita modificar datos del padre, el padre le pasa una **función** como prop:

```jsx
function App() {
  const [count, setCount] = useState(0)

  return <Boton onClick={() => setCount(count + 1)} />
}

function Boton({ onClick }) {
  return <button onClick={onClick}>Sumar</button>
}
```

### Prop drilling

El problema de pasar props a través de múltiples niveles de componentes:

```
App → A → B → C → D (necesita datos de App)
```

Cada nivel intermedio tiene que recibir y reenviar props que no necesita. Soluciones: Context API (lo veremos más adelante) o librerías de estado global como Zustand.

---

## 6. State

El **state** (estado) son datos que el componente gestiona internamente y que pueden cambiar con el tiempo.

### useState

```jsx
const [contador, setContador] = useState(0)
```

- `contador`: valor actual
- `setContador`: función para actualizar el valor
- `useState(0)`: valor inicial

### El estado es inmutable

No se modifica el estado directamente. Siempre se usa la función setter:

```jsx
// ❌ Incorrecto (no provoca re-render)
contador = contador + 1

// ✅ Correcto
setContador(contador + 1)
```

Para objetos y arrays:

```jsx
// ❌ Incorrecto
setUsuario({ ...usuario, nombre: "Ana" })  // esto SÍ funciona para objetos planos
// Pero NO debes mutar el objeto original:
usuario.nombre = "Ana"   // ❌ Esto no funciona

// ✅ Correcto
setUsuario(prev => ({ ...prev, nombre: "Ana" }))
```

### El estado es asíncrono

```jsx
setContador(contador + 1)
console.log(contador)  // ← todavía tiene el valor anterior
```

Si necesitas el nuevo valor inmediatamente, usa el callback:

```jsx
setContador(prev => {
  console.log(prev)  // ← valor actualizado
  return prev + 1
})
```

### Lifting state up

Cuando dos componentes hermanos necesitan compartir estado, el estado **se eleva** al padre común más cercano:

```
App (state: usuario)
 ├── Header (recibe usuario como prop)
 └── Perfil (recibe usuario como prop)
```

---

## 7. useEffect

`useEffect` ejecuta **efectos secundarios** después de que el componente se renderiza.

### ¿Qué se considera efecto secundario?

- Llamadas a API (fetch)
- Suscripciones a eventos
- Modificaciones manuales del DOM
- Timers (setTimeout, setInterval)
- Sincronización con sistemas externos

### Sintaxis

```jsx
useEffect(() => {
  // Código del efecto
  return () => {
    // Cleanup (opcional)
  }
}, [dependencias])
```

### Ciclo de vida

| Sin array de dependencias | Array vacío `[]` | Con dependencias `[var]` |
|---|---|---|
| Se ejecuta en cada render | Se ejecuta solo al montar | Se ejecuta cuando `var` cambia |
| ⚠️ Cuidado: bucles infinitos | ✅ Ideal para fetch inicial | ✅ Ideal para sincronización |

### Cleanup

El cleanup se ejecuta:
1. Cuando el componente se desmonta
2. Antes de re-ejecutar el efecto (si las dependencias cambiaron)

```jsx
useEffect(() => {
  const intervalo = setInterval(() => {
    console.log("tic")
  }, 1000)

  return () => clearInterval(intervalo)  // ← cleanup
}, [])
```

Sin cleanup, cada vez que el componente se re-renderice, se crearía un nuevo intervalo sin eliminar el anterior. Esto causaría **fugas de memoria**.

### Caso común: fetch de datos

```jsx
function Usuarios() {
  const [usuarios, setUsuarios] = useState([])

  useEffect(() => {
    fetch("/api/usuarios")
      .then(res => res.json())
      .then(data => setUsuarios(data))
  }, [])

  return <ul>{usuarios.map(u => <li key={u.id}>{u.nombre}</li>)}</ul>
}
```

### Caso común: escuchar eventos

```jsx
useEffect(() => {
  const handler = () => console.log("redimensionando")
  window.addEventListener("resize", handler)

  return () => window.removeEventListener("resize", handler)
}, [])
```

---

## 8. Hooks

Los **hooks** son funciones que permiten usar estado y otras características de React sin escribir una clase.

### Reglas de los hooks

1. **Solo llamar hooks en el nivel superior** — no dentro de bucles, condiciones o funciones anidadas
2. **Solo llamar hooks desde componentes funcionales o custom hooks** — no desde funciones JavaScript regulares

¿Por qué esta regla? React mantiene un **orden fijo** de hooks por componente. Si un hook se ejecuta condicionalmente, el orden se rompe y React no sabe a qué estado corresponde cada hook.

```jsx
// ❌ Incorrecto
if (activo) {
  useEffect(...)  // el orden cambia si activo es false
}

// ✅ Correcto
useEffect(() => {
  if (activo) { ... }
}, [activo])
```

### Lista completa de hooks nativos

| Hook | Propósito |
|---|---|
| `useState` | Estado local |
| `useEffect` | Efectos secundarios |
| `useContext` | Leer contexto |
| `useRef` | Referencia mutable que persiste entre renders |
| `useMemo` | Valor memoizado (evita cálculos costosos) |
| `useCallback` | Función memoizada |
| `useReducer` | Estado complejo con acciones (como Redux) |
| `useLayoutEffect` | Como useEffect pero síncrono (antes del repintado) |
| `useImperativeHandle` | Exponer métodos a componentes padre |
| `useDebugValue` | Etiquetar custom hooks en React DevTools |
| `useTransition` | Marcar actualizaciones como no urgentes |
| `useDeferredValue` | Versión retrasada de un valor |
| `useId` | ID único para accesibilidad |
| `useSyncExternalStore` | Suscribirse a stores externos |
| `useInsertionEffect` | Para CSS-in-JS |

### Custom hooks

Son funciones que empiezan con `use` y usan hooks nativos internamente. Permiten **extraer lógica repetitiva** de los componentes.

```jsx
// Custom hook
function useFetch(url) {
  const [data, setData] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data)
        setCargando(false)
      })
  }, [url])

  return { data, cargando }
}

// Uso en componente
function Usuarios() {
  const { data, cargando } = useFetch("/api/usuarios")
  if (cargando) return <p>Cargando...</p>
  return <ul>...</ul>
}
```

---

## 9. Context API

Context permite **compartir datos globales** sin pasarlos por props en cada nivel.

### Cuándo usarlo

- Tema (modo claro/oscuro)
- Usuario autenticado
- Idioma/localización
- Preferencias de UI

### Cuándo NO usarlo

Para cosas que cambian con frecuencia (ej: formularios), porque cada cambio en el contexto provoca que **todos** los consumidores se re-rendericen.

### Cómo funciona

```jsx
// 1. Crear el contexto
const TemaContext = createContext("claro")

// 2. Proveer el valor
function App() {
  const [tema, setTema] = useState("claro")
  return (
    <TemaContext.Provider value={{ tema, setTema }}>
      <Toolbar />
    </TemaContext.Provider>
  )
}

// 3. Consumir (en cualquier hijo)
function Boton() {
  const { tema, setTema } = useContext(TemaContext)
  return (
    <button
      style={{ background: tema === "oscuro" ? "#333" : "#fff" }}
      onClick={() => setTema(tema === "claro" ? "oscuro" : "claro")}
    >
      Cambiar tema
    </button>
  )
}
```

### Provider

El `Provider` es el componente que **envuelve** a los consumidores. Puedes tener múltiples Providers anidados, cada uno con su propio contexto.

### Límites de Context

- **No sustituye a un estado global** (Redux, Zustand) para apps complejas
- Causa re-renders innecesarios si no se usa con cuidado
- Para datos que cambian frecuentemente, considera usar `useMemo` o librerías especializadas

---

## 10. React Router

React Router es la librería estándar para navegación SPA (Single Page Application). En una SPA, el navegador **no recarga la página** al cambiar de ruta: solo se re-renderiza el componente correspondiente.

### Conceptos clave

```jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom"

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Inicio</Link>
        <Link to="/usuarios">Usuarios</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/usuarios" element={<Usuarios />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
```

- **BrowserRouter**: Sincroniza la UI con la URL del navegador
- **Routes**: Contenedor que evalúa las rutas (solo renderiza la primera que coincide)
- **Route**: Define un path y el componente a renderizar
- **Link**: Navegación sin recargar la página (a diferencia de `<a href>`)
- **path="*"**: Ruta comodín para 404

### Rutas anidadas

```jsx
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/perfil" element={<Perfil />} />
  </Route>
</Routes>
```

Layout se renderiza siempre, y dentro de él se usa `<Outlet />` para mostrar el contenido de la ruta hija.

### useNavigate

Para redirigir programáticamente (después de un login, por ejemplo):

```jsx
const navigate = useNavigate()

const handleLogin = async () => {
  await login(correo, pass)
  navigate("/dashboard")
}
```

### Parámetros de ruta

```jsx
<Route path="/usuario/:id" element={<UsuarioDetalle />} />

// En UsuarioDetalle:
const { id } = useParams()
```

---

## 11. Fiber — La arquitectura interna de React

Fiber es el **motor de reconciliación** de React desde la versión 16. No es algo que uses directamente, pero entenderlo ayuda a entender por qué React funciona como funciona.

### Problema que resuelve Fiber

En React 15, el proceso de reconciliación era **síncrono y no interrumpible**. Si un componente era muy grande y tardaba 200ms en renderizarse, la UI se congelaba durante esos 200ms. El usuario no podía hacer clic, scrollear o escribir.

### Cómo lo soluciona Fiber

Fiber divide el trabajo en **unidades pequeñas** (fibras) y las procesa de forma **asíncrona**:

1. React comienza a renderizar
2. Cuando encuentra trabajo, lo divide en fibras
3. Después de procesar cada fibra, comprueba si hay trabajo de mayor prioridad (input del usuario, animaciones)
4. Si lo hay, **pausa** el renderizado actual y atiende la tarea urgente
5. Luego **reanuda** donde lo dejó

### Prioridades en React

| Prioridad | Ejemplo |
|---|---|
| Inmediata | Input del usuario, clics |
| Alta | Animaciones |
| Normal | Fetch de datos |
| Baja | Logs, análisis |

Esto permite que React siga siendo **rápido y responsive** incluso con componentes grandes.

### Concurrent Mode (React 18+)

React 18 introdujo funciones que aprovechan Fiber:

- **useTransition**: Marca una actualización como "no urgente". Si el usuario escribe en un input y hay una búsqueda costosa, la búsqueda se retrasa para no bloquear el input.
- **Suspense**: Muestra un fallback mientras se cargan datos o componentes lazy.
- **Automatic batching**: Agrupa múltiples actualizaciones de estado en un solo render.

---

## 12. Patrones en React

### Render props

Un componente recibe una **función como prop** que devuelve JSX:

```jsx
function MouseTracker({ render }) {
  const [pos, setPos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handler = (e) => setPos({ x: e.clientX, y: e.clientY })
    window.addEventListener("mousemove", handler)
    return () => window.removeEventListener("mousemove", handler)
  }, [])

  return render(pos)
}

// Uso
<MouseTracker render={({ x, y }) => (
  <p>El ratón está en {x}, {y}</p>
)} />
```

### Higher-Order Component (HOC)

Una **función que recibe un componente y devuelve un nuevo componente** con funcionalidad añadida:

```jsx
function withAuth(Componente) {
  return function ComponenteAutenticado(props) {
    const { usuario } = useAuth()
    if (!usuario) return <Navigate to="/login" />
    return <Componente {...props} usuario={usuario} />
  }
}

// Uso
const DashboardProtegido = withAuth(Dashboard)
```

### Compound Components

Componentes que trabajan juntos compartiendo estado implícitamente:

```jsx
function Tabs({ children }) {
  const [activa, setActiva] = useState(0)
  return (
    <TabsContext.Provider value={{ activa, setActiva }}>
      {children}
    </TabsContext.Provider>
  )
}

Tabs.Tab = function Tab({ index, children }) {
  const { activa, setActiva } = useContext(TabsContext)
  return (
    <button onClick={() => setActiva(index)} className={activa === index ? "activa" : ""}>
      {children}
    </button>
  )
}

Tabs.Panel = function Panel({ index, children }) {
  const { activa } = useContext(TabsContext)
  return activa === index ? <div>{children}</div> : null
}
```

---

## 13. Rendimiento

### useMemo

Memoiza el **resultado de un cálculo** para no recalcularlo en cada render:

```jsx
const total = useMemo(() => {
  return items.reduce((sum, item) => sum + item.precio, 0)
}, [items])  // Solo recalcula cuando items cambia
```

### useCallback

Memoiza una **función** para no crearla de nuevo en cada render:

```jsx
const handleClick = useCallback(() => {
  setContador(c => c + 1)
}, [])  // La función es siempre la misma
```

### React.memo

Evita que un componente se re-renderice si sus props no han cambiado:

```jsx
const ListaItem = React.memo(function ListaItem({ item }) {
  return <li>{item.nombre}</li>
})
```

### Lazy loading

Carga componentes solo cuando se necesitan:

```jsx
const Dashboard = lazy(() => import("./pages/Dashboard"))

<Suspense fallback={<p>Cargando...</p>}>
  <Dashboard />
</Suspense>
```

### Regla de oro del rendimiento en React

**No optimices prematuramente.** Primero escribe código claro y funcional. Si detectas un problema de rendimiento (con React DevTools Profiler), entonces aplica `useMemo`, `useCallback` o `React.memo`.

---

## 14. Testing

### React Testing Library (RTL)

Es la librería recomendada por React para testing. Su filosofía: **testear el comportamiento, no la implementación**.

```jsx
import { render, screen, fireEvent } from "@testing-library/react"

test("muestra el nombre del usuario", () => {
  render(<Saludo nombre="Ana" />)
  expect(screen.getByText("Hola, Ana")).toBeInTheDocument()
})
```

### Lo que NO se debe testear

- Estado interno (no importa cómo se almacena, sino qué ve el usuario)
- Métodos privados
- Detalles de implementación (nombres de clases CSS, estructura del DOM)

### Lo que SÍ se debe testear

- Comportamiento visible para el usuario
- Flujos críticos (login, registro, checkout)
- Casos límite (errores, datos vacíos)

---

## 15. Conceptos que NO están en este proyecto pero deberías conocer

### Server Components (React 19+)

React Server Components permiten renderizar componentes **en el servidor** y enviar solo el HTML al cliente. Ventajas:

- Menos JavaScript enviado al navegador
- Acceso directo a la base de datos (sin API REST)
- Carga inicial más rápida

Next.js App Router usa Server Components por defecto.

### Suspense

Permite mostrar un **fallback** mientras se carga contenido asíncrono:

```jsx
<Suspense fallback={<Spinner />}>
  <UsuarioDetalle id={id} />
</Suspense>
```

### Error Boundaries

Componentes que capturan errores en el renderizado de sus hijos y muestran una UI alternativa (sin romper toda la app):

```jsx
class ErrorBoundary extends React.Component {
  state = { error: null }
  static getDerivedStateFromError(error) {
    return { error }
  }
  render() {
    if (this.state.error) return <h1>Algo salio mal</h1>
    return this.props.children
  }
}
```

### Portals

Renderizan un componente fuera del DOM del padre (útil para modales, tooltips, popovers):

```jsx
createPortal(<Modal />, document.getElementById("modal-root"))
```

### StrictMode

React 18+ renderiza los componentes dos veces en desarrollo para detectar efectos secundarios. No afecta a producción.

---

## Resumen

React es una librería simple en concepto (componentes + estado + Virtual DOM) pero con un ecosistema rico que resuelve problemas complejos. Las ideas clave:

1. **Componentes**: la UI se divide en piezas reutilizables
2. **Estado inmutable**: no se modifica, se reemplaza
3. **Flujo unidireccional**: los datos bajan de padre a hijo
4. **Virtual DOM**: cambios eficientes en la interfaz
5. **Hooks**: estado y efectos en componentes funcionales
6. **Composición**: se construye combinando componentes pequeños
